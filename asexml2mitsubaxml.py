import time
import xml.etree.cElementTree as etree
import xml.dom.minidom as dom

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
	curr_camera.set("type", "perspective") # by default it's gonna be perspective

	# Go into transform
	transf_camera = etree.SubElement(curr_camera, "transform")
	transf_camera.set("name", "toWorld")
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
	elif(camera_type=="Free"):
		transl_camera = etree.SubElement(transf_camera, "translate")
		print("FREE CAMERA UNFINISHED")
	else:
		print("Camera type unknown : "+camera_type)
	# The default fov is 60 for max, and in the ase the fov is just the factor to multiply 60
	fov = 60 * float(camera.getElementsByTagName("CAMERA_SETTINGS")[0].getAttribute("CAMERA_FOV"))
	camera_fov = etree.SubElement(curr_camera, "float")
	camera_fov.set("name", "fov")
	camera_fov.set("value", str(fov))
	# Max expresses the the vertical fov
	camera_fov_axis = etree.SubElement(curr_camera, "string")
	camera_fov_axis.set("name", "fovAxis")
	camera_fov_axis.set("value", "y")

# Set up lights
for light in inputdata.getElementsByTagName("LIGHTOBJECT") :
	light_name = light.getAttribute("NODE_NAME")
	# There should be only one node for pointlight. Maybe not for more complex light, TODO
	node = light.getElementsByTagName("NODE_TM")[0]
	light_pos = node.getAttribute("TM_POS").split()
	light_parameters = light.getElementsByTagName("LIGHT_SETTINGS")[0]
	light_color = light_parameters.getAttribute("LIGHT_COLOR")
	light_intensity = light_parameters.getAttribute("LIGHT_INTENS")

	light_in_scene = etree.SubElement(root, "emitter")
	light_in_scene.set("type", "point")
	light_in_scene.set("id",light_name)
	light_color_in_scene = etree.SubElement(light_in_scene, "spectrum")
	light_color_in_scene.set("name", "intensity")
	light_color_in_scene.set("value", light_color)

	light_transform_in_scene = etree.SubElement(light_in_scene, "transform")
	light_transform_in_scene.set("name","toWorld")
	light_translate_in_scene = etree.SubElement(light_transform_in_scene, "translate")
	light_translate_in_scene.set("x", light_pos[0])
	light_translate_in_scene.set("y", light_pos[1])
	light_translate_in_scene.set("z", light_pos[2])

	# <rgb name="spectrumProperty" value="0.2,0.8,0.4"/>

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


# Dirty workaround to import temporary obj and test
shape = etree.SubElement(root, "shape")
shape.set("type", "obj")
importshape = etree.SubElement(shape, "string")
importshape.set("name", "filename")
importshape.set("value", "simplecube.obj")






tree = etree.ElementTree(root)
tree.write("simplecubemitsuba.xml")


xmlstr = dom.parse("simplecubemitsuba.xml")

# print(xmlstr.toprettyxml())
outputfile = open("simplecubemitsuba.xml", "w")
outputfile.write(xmlstr.toprettyxml())

# time.sleep(1)
