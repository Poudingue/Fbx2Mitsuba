import math
import tools
import config
import xml.etree.ElementTree as etree

def build(root, nodes, models) :
	verbose = config.verbose
	debug   = config.debug

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

		if "3dsMax|FSphereExtParameters|light_radius" in light_node :
			light_is_a_sphere = True
			sphere_radius = float(light_node["3dsMax|FSphereExtParameters|light_radius"][-1])
		else :
			light_is_a_sphere = False

		if "3dsMax|FAreaParameters" in light_node :
			print("Area lights not supported, light with id "+id+"will be considered as a point light")
			colors = light_node["Color"][-3:] if "Color" in light_node else ["1","1","1"]
		elif light_node["3dsMax|"+("FSphereParameters"if light_is_a_sphere else "FPointParameters")+"|useKelvin"][-1] == "1" :
			colors = tools.kelvin2rgb(float(light_node["3dsMax|"+("FSphereParameters"if light_is_a_sphere else "FPointParameters")+"|kelvin"][-1]))
		else :
			colors = light_node["Color"][-3:] if "Color" in light_node else ["1"]

		# Divide intensity by apparent surface of the sphere if it's not a point
		intensity = float(light_node["Intensity"][-1])/(2.*math.pi*sphere_radius**2. if light_is_a_sphere else 1)
		rvb = []
		for color in colors :
			rvb.append(str(intensity * float(color)))

		if light_is_a_sphere :
			light_shape = tools.create_obj(root, "shape", "sphere")
			tools.set_value(light_shape, "float", "radius", str(sphere_radius))

		light = tools.create_obj(
			parent = light_shape if light_is_a_sphere else root,
			object = "emitter",
			type   = "area" if light_is_a_sphere else "point"
		)

		tools.set_value(light, "spectrum", "radiance" if light_is_a_sphere else "intensity", " ".join(rvb))

		tools.transform_object(light_shape if light_is_a_sphere else light, light_model)

	# Handle cameras

	if len(camera_nodes) != len(camera_models) :
		print("nb of camera nodes and camera models not the same")
		exit(0)

	for camera_node in camera_nodes :

		curr_camera = tools.create_obj(root, "sensor", "perspective")
		# by default it's gonna be perspective. TODO handle other types of camera

		# Set up with nice default values. TODO parameters to control this
		curr_film = tools.create_obj(curr_camera, "film", "hdrfilm")
		tools.set_value(curr_film, "integer",  "width", camera_node["AspectWidth"][-1])
		tools.set_value(curr_film, "integer", "height", camera_node["AspectHeight"][-1])

		rfilter = tools.create_obj(curr_film, "rfilter", "gaussian")

		# Set up with nice values. TODO parameters to control
		curr_sampler = tools.create_obj(curr_camera, "sampler", "ldsampler")
		tools.set_value(curr_sampler, "integer", "sampleCount", "64")

		# Go into transform
		transf_camera = tools.create_obj(curr_camera, "transform", "toWorld")

		lookat_camera = etree.SubElement(transf_camera, "lookat")
		lookat_camera.set("origin", " ".join(camera_node["Position"][-3:]))
		lookat_camera.set("target", " ".join(camera_node["InterestPosition"][-3:]))
		lookat_camera.set("up",     " ".join(camera_node["UpVector"][-3:]))

		tools.set_value(curr_camera, "float", "fov", camera_node["FieldOfView"][-1])
		tools.set_value(curr_camera, "string", "fovAxis", "x")# Max expresses the horizontal fov

	return
