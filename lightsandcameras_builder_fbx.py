import tools
import xml.etree.ElementTree as etree

def build(root, nodes, models, verbose = False, debug = False) :

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

	if len(camera_nodes) != len(camera_models) :
		print("nb of camera nodes and camera models not the same")
	if len(light_nodes) != len(light_models) :
		print("nb of light nodes and light models not the same")

# Handle lights

	for i in range(len(light_nodes)) :
		light_node, light_model = light_nodes[i], light_models[i]

		light_pos = light_model["LclTranslation"].split(",")[-3:]
		print("Light pos : "+str(light_pos))

		colors = light_node["Color"].split(",")[-3:]
		intensity = float(light_node["Intensity"].split(",")[-1])
		rvb = []
		for color in colors :
			rvb.append(str(intensity * float(color)))

		if "3dsMax|FSphereExtParameters|light_radius" in light_node :
			light_is_a_sphere = True
			sphere_radius = light_node["3dsMax|FSphereExtParameters|light_radius"]
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

	for camera_node in camera_nodes :
		pass

	return
