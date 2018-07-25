import os
import tools
import lightsandcameras_builder_fbx
import textures_builder_fbx
import materials_builder_fbx
import shapes_builder_fbx
import models_builder_fbx
import xml.etree.ElementTree as etree

def build(filename, fbxtree, verbose = False, debug = False, closest = False, realist = False):
	if verbose : print("plybuilder launched")
	if not os.path.exists("materials") :
		os.makedirs("materials")

	objects = fbxtree.find("Objects")

	models    = objects.findall("Model")
	geometries  = objects.findall("Geometry")
	materials = objects.findall("Material")
	nodes     = objects.findall("NodeAttribute") # Include cameras and lights
	videos    = objects.findall("Video") # Not sure about what it contains
	textures  = objects.findall("Texture")
	# Animation. Will probably not be usable, but collect anyway
	anim_c_n  = objects.findall("AnimationCurveNode")
	anim_c    = objects.findall("AnimationCurve")

	implem    = objects.find("Implementation")
	bind_table= objects.find("BindingTable")
	bind_oper = objects.find("BindingOperator")

	connections_list = fbxtree.find("Connections")
	# Comments contain infos about links between objects and their type
	comments = connections_list.findall("comment")
	links    = connections_list.findall("C")
	links_simple, links_revert, links_param = tools.extract_links(links)

	root = etree.Element("scene")
	root.set("version", "0.5.0")

	# Set up the integrator. I chose pathtracing by default.
	integrator = etree.SubElement(root, "integrator")
	integrator.set("type", "path")

	lightsandcameras_builder_fbx.build(root, nodes, models, verbose, debug)
	textures_id = textures_builder_fbx.build(root, textures, verbose, debug)
	materials_ids = materials_builder_fbx.build(root, materials, textures_id, links_param, verbose, debug, closest)
	shapes_ids = shapes_builder_fbx.build(root, geometries, materials_ids, links_simple, links_revert, verbose, debug)
	models_builder_fbx.build(root, models, links_simple, shapes_ids, verbose, debug)

	if verbose : print("Writing to file…")
	with open(filename+".xml", "w", encoding="utf8") as outputfile :
		if verbose : print("prettifying… (Can take a while for big files)")
		stringout = tools.prettifyXml(etree.tostring(root).decode())
		if verbose : print("writing…")
		outputfile.write(stringout)

	if verbose : print("End of builder_fromfbx for now")
