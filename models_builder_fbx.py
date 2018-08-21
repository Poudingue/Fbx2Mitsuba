import os
from copy import deepcopy
import tools
import config
import xml.etree.ElementTree as etree

# Useful to retrieve the transform from all the hierarchy of the scene.
def recursive_build_hierarchy(root, shapes_ids, object, links_simple, links_revert, models_id, id) :
	if id in links_revert :
		for parent_id in links_revert[id] : # If multiple parents, multiple instances of the object must be created.
			current_object = deepcopy(object)
			tools.transform_object(current_object, models_id[id])
			if parent_id == "0" : # End recursion and add the transformation
				root.append(current_object)
			else :
				recursive_build_hierarchy(root, shapes_ids, current_object, links_simple, links_revert, models_id, parent_id)


def build(root, models, links_simple, links_revert, shapes_ids):
	if config.verbose : print("models_builder_fbx launched")

	comment = etree.Comment("Models.")
	root.append(comment)

	# Create a dictionnary of models to pass through every parent
	models_id = {}
	for model in models :
		id, type, obj = model.get("value").replace("::","").split(",")
		models_id[id] = tools.getProperties(model)

	for model in models :
		id, type, obj = model.get("value").replace("::","").split(",")
		if id in links_simple :
			for link in links_simple[id] :
				if link in shapes_ids : # Only shapes (for now ?)
					curr_shape = etree.Element("shape")
					curr_shape.set("type", "instance")
					curr_ref = etree.SubElement(curr_shape, "ref")
					curr_ref.set("id", link)
					recursive_build_hierarchy(root, shapes_ids, curr_shape, links_simple, links_revert, models_id, id)


		elif config.verbose :
			print("id "+id+" not in links_simple")
