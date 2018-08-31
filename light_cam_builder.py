import math
import tools
import config
import xml.etree.ElementTree as etree

def build(root, nodes, models, nulls, links_simple, links_param) :
	"""
	Creates lights and cameras in the scene
	"""
	verbose = config.verbose
	debug   = config.debug
	if verbose : print("lightsandcameras_builder_fbx launched")

	comment = etree.Comment("Lights and cameras")
	root.append(comment)

	# Prepare nodes properties referenced by id for easy access
	camera_nodes, light_nodes = {}, {}
	for node in nodes :
		id, type, obj = node.get("value").replace("::","").split(", ")
		properties = tools.getProperties(node)
		# named by id to find easily when needed
		node.tag = id
		if   obj == "Camera" :
			camera_nodes[id] = properties
		elif obj == "Light"  :
			light_nodes[id]  = properties

	# Prepare models properties referenced by id for easy access
	camera_models, light_models, null_models = {}, {}, {}
	for model in models :
		id, type, obj = model.get("value").replace("::","").split(", ")
		properties = tools.getProperties(model)
		# named by id to find easily when needed
		node.tag = id
		if   obj == "Camera" :
			camera_models[id] = properties
		elif obj == "Light"  :
			light_models[id]  = properties
		elif obj == "Null"   :
			null_models[id]   = properties

	# Lights
	# Every light placed in the scene is referenced by a model.
	# This model should be linked to a node containing all the light's properties.
	# Once we retrieved it, we are able to create the light correctly
	for id, light_model in light_models.items() :
		if len(links_simple[id]) != 1 :
			print("light_cam_builder_fbx : "+len(links_simple[id])+" node(s) for light model "+id)
		light_node = light_nodes[links_simple[id][0]]

		light_is_a_spot = "LookAtProperty" in links_param[id] # LightType is present when the light has a target

		if "3dsMax|FSphereExtParameters|light_radius" in light_node : # This parameter means that the light is a sphere
			light_is_a_sphere = True
			sphere_radius = float(light_node["3dsMax|FSphereExtParameters|light_radius"][-1])
		else : light_is_a_sphere = False

		# This is a mess. TODO clean all this, it's not legible
		if "3dsMax|FAreaParameters" in light_node : #TODO area lights
			print("Area lights not supported yet, light with id "+id+"will be considered as a point light for now")
			colors = light_node["Color"][-3:] if "Color" in light_node else ["1","1","1"]
		elif light_node["3dsMax|"+(("T" if light_is_a_spot else "F")+("Sphere" if light_is_a_sphere else "Point")+"Parameters")+"|useKelvin"][-1] == "1" :
			colors = tools.kelvin2rgb(float(light_node["3dsMax|"+("FSphereParameters"if light_is_a_sphere else "FPointParameters")+"|kelvin"][-1]))
			# TODO color filter
		else :
			colors = light_node["Color"][-3:] if "Color" in light_node else ["1"]

		# Divide intensity by apparent surface of the sphere (disc) if it's not a point
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
			type   = "spot" if light_is_a_spot else "area" if light_is_a_sphere else "point"
		)

		tools.set_value(light, "spectrum", "radiance" if light_is_a_sphere and not light_is_a_spot else "intensity", " ".join(rvb))

		if light_is_a_spot  :
			# angles are divided by 2 because 3dsMax expresses the total angle, and mitsuba the angle from the center of the ray
			tools.set_value(light, "float", "cutoffAngle", str(.5*float(light_node["OuterAngle"][-1])))
			tools.set_value(light, "float", "beamWidth",   str(.5*float(light_node["InnerAngle"][-1])))
			tools.transform_lookat(
				light,
				" ".join(light_model["Lcl Translation"][-3:]),
				" ".join(null_models[links_param[id]["LookAtProperty"]]["Lcl Translation"][-3:])
				)
		else :
			tools.transform_object(light_shape if light_is_a_sphere else light, light_model)


	# Handle cameras
	for id, camera_model in camera_models.items() :
		if len(links_simple[id]) != 1 :
			print("light_cam_builder_fbx : "+str(len(links_simple[id]))+" node(s) for camera model "+id)
		camera_node = camera_nodes[links_simple[id][0]]
		curr_camera = tools.create_obj(root, "sensor", "perspective")

		curr_film = tools.create_obj(curr_camera, "film", "hdrfilm")
		tools.set_value(curr_film, "integer",  "width", camera_node["AspectWidth"][-1])
		tools.set_value(curr_film, "integer", "height", camera_node["AspectHeight"][-1])

		rfilter = tools.create_obj(curr_film, "rfilter", "box")

		# Set up with nice values. TODO parameters to control this
		curr_sampler = tools.create_obj(curr_camera, "sampler", "ldsampler")
		tools.set_value(curr_sampler, "integer", "sampleCount", "64")

		tools.transform_lookat_from_properties(curr_camera, camera_node)

		tools.set_value(curr_camera, "float", "fov", camera_node["FieldOfView"][-1])
		tools.set_value(curr_camera, "string", "fovAxis", "x")# Max expresses the horizontal fov
