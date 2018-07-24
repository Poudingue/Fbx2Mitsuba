import tools
import xml.etree.ElementTree as etree

def build(root, nodes, models, verbose = False, debug = False) :
	if verbose : print("lightsandcameras_builder_fbx launched")

	comment = etree.Comment("Lights and cameras")
	root.append(comment)
	# Prepare nodes and models properties for easy access
	camera_nodes, light_nodes = [], []
	for node in nodes :
		id, type, obj = node.get("value").replace("::","").split(", ")
		properties = tools.getProperties(node)
		# named by id to find easily when needed
		node.tag = id
		if obj == "Camera" :
			camera_nodes.append(properties)
		elif obj == "Light" :
			light_nodes.append(properties)

	camera_models, light_models = [], []

	for model in models :
		id, type, obj = model.get("value").replace("::","").split(", ")
		properties = tools.getProperties(model)
		# named by id to find easily when needed
		node.tag = id
		if obj == "Camera" :
			camera_models.append(properties)
		elif obj == "Light" :
			light_models.append(properties)

	# Handle lights

	if len(light_nodes) != len(light_models) :
		print("nb of light nodes and light models not the same")
		exit(0)

	for i in range(len(light_nodes)) :
		light_node, light_model = light_nodes[i], light_models[i]

		light_pos = light_model["LclTranslation"][-3:]

		colors = light_node["Color"][-3:]
		intensity = float(light_node["Intensity"][-1])
		rvb = []
		for color in colors :
			rvb.append(str(intensity * float(color)))

		if "3dsMax|FSphereExtParameters|light_radius" in light_node :
			light_is_a_sphere = True
			sphere_radius = light_node["3dsMax|FSphereExtParameters|light_radius"][-1]
		else : light_is_a_sphere = False

		if light_is_a_sphere :
			light_shape = etree.SubElement(root, "shape")
			light_shape.set("type", "sphere")
			light_radius = etree.SubElement(light_shape, "float")
			light_radius.set("name", "radius")
			light_radius.set("value", sphere_radius)

		light = etree.SubElement(light_shape if light_is_a_sphere else root, "emitter")
		light.set("type", "area" if light_is_a_sphere else "point")
		light_color = etree.SubElement(light, "spectrum")
		light_color.set("name", "radiance" if light_is_a_sphere else "intensity")
		light_color.set("value", " ".join(rvb))

		light_transform = etree.SubElement(light_shape if light_is_a_sphere else light, "transform")
		light_transform.set("name","toWorld")

		light_translate = etree.SubElement(light_transform if light_is_a_sphere else light_transform, "translate")
		light_translate.set("x", str(light_pos[0]))
		light_translate.set("y", str(light_pos[1]))
		light_translate.set("z", str(light_pos[2]))

	# Handle cameras

	if len(camera_nodes) != len(camera_models) :
		print("nb of camera nodes and camera models not the same")
		exit(0)

	for camera_node in camera_nodes :

		curr_camera = etree.SubElement(root, "sensor")
		# by default it's gonna be perspective. TODO handle other types of camera
		curr_camera.set("type", "perspective")

		# Set up with nice default values. TODO parameters to control this
		curr_film = etree.SubElement(curr_camera, "film")
		curr_film.set("type", "hdrfilm")
		curr_width = etree.SubElement(curr_film, "integer")
		curr_width.set("name", "width")
		curr_width.set("value", camera_node["AspectWidth"][-1])

		curr_height = etree.SubElement(curr_film, "integer")
		curr_height.set("name", "height")
		curr_height.set("value", camera_node["AspectHeight"][-1])
		rfilter = etree.SubElement(curr_film, "rfilter")
		rfilter.set("type", "gaussian")

		# Set up with nice values. TODO parameters to control
		curr_sampler = etree.SubElement(curr_camera, "sampler")
		curr_sampler.set("type", "ldsampler")
		sample_count = etree.SubElement(curr_sampler, "integer")
		sample_count.set("name", "sampleCount")
		sample_count.set("value", "64")

		# Go into transform
		transf_camera = etree.SubElement(curr_camera, "transform")
		transf_camera.set("name", "toWorld")

		lookat_camera = etree.SubElement(transf_camera, "lookat")
		lookat_camera.set("origin", " ".join(camera_node["Position"][-3:]))
		lookat_camera.set("target", " ".join(camera_node["InterestPosition"][-3:]))
		lookat_camera.set("up",     " ".join(camera_node["UpVector"][-3:]))

		camera_fov = etree.SubElement(curr_camera, "float")
		camera_fov.set("name", "fov")
		camera_fov.set("value", camera_node["FieldOfView"][-1])
		# Max expresses the vertical fov
		camera_fov_axis = etree.SubElement(curr_camera, "string")
		camera_fov_axis.set("name", "fovAxis")
		camera_fov_axis.set("value", "x")


	return
