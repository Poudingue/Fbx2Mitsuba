import os
import tools
import light_cam_builder_fbx
import textures_builder_fbx
import materials_builder_fbx
import shapes_builder_fbx
import models_builder_fbx
import xml.etree.ElementTree as etree
import config

def build(fbxtree):
	verbose = config.verbose
	if verbose : print("builder_fromfbx launched")

	globalsettings = tools.getProperties(fbxtree.find("GlobalSettings"))
	config.upvector = "0 1 0" if globalsettings["UpAxis"][-1] == "1" else "0 0 1"

	objects = fbxtree.find("Objects")

	# Separate objects into different categories
	models    = objects.findall("Model")
	geometries= objects.findall("Geometry")
	materials = objects.findall("Material")
	nodes     = objects.findall("NodeAttribute") # Include cameras and lights
	videos    = objects.findall("Video") # Not sure about what it contains, it seems to be a duplicate of “textures”. Maybe for compatibility reasons ?
	textures  = objects.findall("Texture")
	nulls     = objects.findall("Null") # Useful for cameras and spot targets

	""" Useless for now
	# Animation. Will probably not be usable
	anim_c_n  = objects.findall("AnimationCurveNode")
	anim_c    = objects.findall("AnimationCurve")

	# Maybe useful. Not sure what to do with this.
	implem    = objects.find("Implementation")
	bind_table= objects.find("BindingTable")
	bind_oper = objects.find("BindingOperator")
	"""

	# Useful to link objects, textures to materials, materials to models, and geometry to models.
	connections_list = fbxtree.find("Connections")
	comments = connections_list.findall("comment")
	links    = connections_list.findall("C")
	# Stocking links between objects.
	# Links simple and links revert are simple links, for example for hierarchies of objects.
	# Links param and links param revert are for parameters, for example, a texture referenced by a material.
	links_simple, links_revert, links_param, links_param_revert = tools.extract_links(links)

	root = etree.Element("scene")
	root.set("version", "0.5.0")

	# Set up the integrator. I chose pathtracing by default TODO add as a parameter
	tools.create_obj(root, "integrator", "path")

	# All the functions will directly add their elements to the root element
	light_cam_ids = light_cam_builder_fbx.build(root, nodes, models, nulls, links_simple, links_param)
	textures_id   =  textures_builder_fbx.build(root, textures, links_param_revert)
	materials_ids = materials_builder_fbx.build(root, materials, textures_id, links_param, links_param_revert)
	shapes_ids    =    shapes_builder_fbx.build(root, geometries, materials_ids, links_simple, links_revert)
	models_builder_fbx.build(root, models, links_simple, links_revert, shapes_ids)

	if verbose : print("Writing to file…")
	with open(config.filename+".xml", "w", encoding="utf8") as outputfile :
		if verbose : print("prettifying… (Can take a while for big files)")
		stringout = tools.prettifyXml(etree.tostring(root).decode())
		if verbose : print("writing…")
		outputfile.write(stringout)
