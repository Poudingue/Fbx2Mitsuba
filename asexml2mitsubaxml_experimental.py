import time
import re
import xml.etree.cElementTree as etree
import xml.dom.minidom as dom

# For complementary infos not in the ase file
inputfbx = open("simplecube.fbx", "r")

inputfile = open("simplecubease.xml", "r")
inputdata = dom.parse(inputfile)
inputfile.close()

root = etree.Element("scene")

root.set("version", "0.5.0")

# Set up cameras

for camera in inputdata.getElementsByTagName("CAMERAOBJECT") :
	# Go into camera
	camera_name = camera.getAttribute("NODE_NAME")
	camera_type = camera.getAttribute("CAMERA_TYPE")
	curr_camera = etree.SubElement(root, "sensor")
	curr_camera.set("type", "perspective") # by default it's gonna be perspective.

	# Set up with nice default values. Should be parameters
	curr_film = etree.SubElement(curr_camera, "film")
	curr_film.set("type", "hdrfilm")
	curr_width = etree.SubElement(curr_film, "integer")
	curr_width.set("name", "width")
	curr_width.set("value", "1600")
	curr_height = etree.SubElement(curr_film, "integer")
	curr_height.set("name", "height")
	curr_height.set("value", "900")
	rfilter = etree.SubElement(curr_film, "rfilter")
	rfilter.set("type", "gaussian")

	curr_sampler = etree.SubElement(curr_camera, "sampler")
	curr_sampler.set("type", "ldsampler")
	sample_count = etree.SubElement(curr_sampler, "integer")
	sample_count.set("name", "sampleCount")
	sample_count.set("value", "64")

	# Go into transform
	transf_camera = etree.SubElement(curr_camera, "transform")
	transf_camera.set("name", "toWorld")
	# 3dsmax camera seems to be left-handed.
	# left_handed = etree.SubElement(transf_camera, "scale")
	# left_handed.set("x", "-1")
	if(camera_type=="Target"):
		lookat_camera = etree.SubElement(transf_camera, "lookat")
		origin = "INVALID ORIGIN"
		target = "INVALID TARGET"
		for node in camera.getElementsByTagName("NODE_TM"):
			node_name = node.getAttribute("NODE_NAME")
			if node_name==camera_name :
				origin = node.getAttribute("TM_POS")
			elif node_name==camera_name+".Target" :
				target = node.getAttribute("TM_POS")
			else :
				print("UNKNOWN CAMERA NODE :\ncamera : "+camera_name+"\nnode : "+node_name)
		if origin == "INVALID ORIGIN" or target == "INVALID TARGET":
			print("INVALID ORIGIN OR TARGET for camera "+camera_name)

		lookat_camera.set("origin", origin)
		lookat_camera.set("target", target)
		# We need to specify the «up» direction. In 3dsmax it's y.
		# Won't work with tilted camera yet, to be fixed
		lookat_camera.set("up", "0, 0, 1")
	elif(camera_type=="Free"):
		transl_camera = etree.SubElement(transf_camera, "translate")
		coordinates = origin.split()
		print("FREE CAMERA COORD :\nx: "+coordinates[0]+" y: "+coordinates[1]+" z: "+coordinates[2])
		transl_camera.set("x", coordinates[0])
		transl_camera.set("y", coordinates[1])
		transl_camera.set("z", coordinates[2])
		print("FREE CAMERA UNFINISHED")
	else:
		print("Camera type unknown : "+camera_type)
	# The real angle can be accessed in the fbx file for some elements, it allowed me to chose the right multiplier
	fov = 57.29677533 * float(camera.getElementsByTagName("CAMERA_SETTINGS")[0].getAttribute("CAMERA_FOV"))
	camera_fov = etree.SubElement(curr_camera, "float")
	camera_fov.set("name", "fov")
	camera_fov.set("value", str(fov))
	# Max expresses the vertical fov
	camera_fov_axis = etree.SubElement(curr_camera, "string")
	camera_fov_axis.set("name", "fovAxis")
	camera_fov_axis.set("value", "x")

# Set up lights
for light in inputdata.getElementsByTagName("LIGHTOBJECT") :
	light_name = light.getAttribute("NODE_NAME")

	# TODO a better method to search for stuff in the FBX. Probably convert it to xml

	# Search for the light reference in the fbx file
	light_ref = ""
	nexturn = False
	for line in open("simplecube.fbx", "r") :
		if nexturn :
			reg_lightref = re.match("\tC: \"OO\",(\d*),\d*\n", line)
			if reg_lightref!=None :
				light_ref = reg_lightref[1]
			else :
				print("LIGHT REFERENCE NOT FOUND : "+light_name)
			break
		if line == "\t;NodeAttribute::, Model::"+light_name+"\n":
			nexturn = True

	if light_ref=="" :
		print("Light not found in fbx : "+light_name)

	# Searching in the FBX file for sphere light source
	light_is_a_sphere = False
	sphere_radius = 0
	searchBegan = False
	for line in open("simplecube.fbx", "r") :
		if searchBegan and not (line.startswith("\t\tProperties70:") or line.startswith("\t\t\tP: ")):
			break
		if searchBegan :
			if "FSphereParameters" in line :
				light_is_a_sphere = True
			if "FSphereExtParameters|light_radius" in line :
				radius_extraction = line.split(",")
				sphere_radius = radius_extraction[len(radius_extraction)-1]#
		reg_lightdef = re.match("\tNodeAttribute: "+light_ref+", \"NodeAttribute::\", \"Light\" {", line)
		if reg_lightdef!=None:
			searchBegan = True

	# There should be only one node for pointlight. Maybe not for more complex light, TODO
	node = light.getElementsByTagName("NODE_TM")[0]
	light_pos = node.getAttribute("TM_POS").split()
	light_parameters = light.getElementsByTagName("LIGHT_SETTINGS")[0]
	light_color = light_parameters.getAttribute("LIGHT_COLOR").split()
	# With arbitrary tries, it seems that multiplying by 10000 the light intensity is the way to go
	colors = ""
	for component in light_color :
		colors += " " + str(float(component)*1000/(float(sphere_radius)**2) if light_is_a_sphere else float(component)*1000)


	light_intensity = light_parameters.getAttribute("LIGHT_INTENS")

	if light_is_a_sphere :
		light_shape = etree.SubElement(root, "shape")
		light_shape.set("type", "sphere")
		light_radius = etree.SubElement(light_shape, "float")
		light_radius.set("name", "radius")
		light_radius.set("value", sphere_radius)
		light_in_scene = etree.SubElement(light_shape, "emitter")
	else :
		light_in_scene = etree.SubElement(root, "emitter")

	light_in_scene.set("type", "area" if light_is_a_sphere else "point")

	light_in_scene.set("id",light_name)
	light_color_in_scene = etree.SubElement(light_in_scene, "spectrum")
	light_color_in_scene.set("name", "radiance" if light_is_a_sphere else "intensity")
	light_color_in_scene.set("value", colors.strip())

	light_transform_in_scene = etree.SubElement(light_shape if light_is_a_sphere else light_in_scene, "transform")
	light_transform_in_scene.set("name","toWorld")
	light_translate_in_scene = etree.SubElement(light_transform_in_scene, "translate")

	light_translate_in_scene.set("x", light_pos[0])
	light_translate_in_scene.set("y", light_pos[1])
	light_translate_in_scene.set("z", light_pos[2])

# Environnement lighting -> We take the skybox from the 3dsmax scene
# There should be only one in the file
envmap = inputdata.getElementsByTagName("SCENE_ENVMAP")
if envmap==[] :
	print("No envmap")
else :
	bitmap_location = envmap[0].getAttribute("BITMAP")
	if bitmap_location=="":
		print("ONLY IMAGES ARE SUPPORTED FOR ENVIRONNEMENT MAP")
	else:
		envmap_scene = etree.SubElement(root, "emitter")
		envmap_scene.set("type","envmap")
		envmap_scene.set("id", envmap[0].getAttribute("MAP_NAME"))

		envmap_scene_texture = etree.SubElement(envmap_scene, "string")
		envmap_scene_texture.set("name","filename")
		envmap_scene_texture.set("value",bitmap_location)

		# rotation and simmetry to match the orientation in original 3dsmax scene
		envmap_scene_transf = etree.SubElement(envmap_scene, "transform")
		envmap_scene_transf.set("name", "toWorld")
		envmap_scene_rotat = etree.SubElement(envmap_scene_transf, "rotate")
		envmap_scene_rotat.set("x", "1")
		envmap_scene_rotat.set("angle", "90")
		envmap_scene_scale = etree.SubElement(envmap_scene_transf, "scale")
		envmap_scene_scale.set("x", "-1")

		# arbitrary value to darken the environnement. Should be a parameter
		envmap_brightness = etree.SubElement(envmap_scene, "float")
		envmap_brightness.set("name", "scale")
		envmap_brightness.set("value", "1")


# import .ply exported by plybuilder.py
for geomobject in inputdata.getElementsByTagName("GEOMOBJECT") :
	name =  geomobject.getAttribute("NODE_NAME")
	shape = etree.SubElement(root, "shape")
	shape.set("type", "ply")
	importshape = etree.SubElement(shape, "string")
	importshape.set("name", "filename")
	importshape.set("value", "meshes/"+name+".ply")
	shape_transf = etree.SubElement(shape, "transform")
	shape_transf.set("name", "toWorld")

tree = etree.ElementTree(root)
tree.write("simplecubemitsuba.xml")

xmlstr = dom.parse("simplecubemitsuba.xml")

outputfile = open("simplecubemitsuba.xml", "w")
outputfile.write(xmlstr.toprettyxml())

# time.sleep(1)
