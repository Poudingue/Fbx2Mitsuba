import os
import tools
import ply_builder_fbx
import lightsandcameras_builder_fbx
import xml.etree.ElementTree as etree

def build(filename, fbxtree, verbose = False, debug = False):
	if verbose : print("plybuilder launched")
	if not os.path.exists("materials") :
		os.makedirs("materials")

	objects = fbxtree.find("Objects")

	models    = objects.findall("Model")
	geometry  = objects.findall("Geometry")
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

	root = etree.Element("scene")
	root.set("version", "0.5.0")

	# Set up the integrator. I chose pathtracing by default.
	integrator = etree.SubElement(root, "integrator")
	integrator.set("type", "path")

	# if not os.path.exists("meshes") :
	# 	os.makedirs("meshes")
	# ply_builder_fbx.build(geometry, verbose, debug)

	lightsandcameras_builder_fbx.build(root, nodes, models, verbose, debug)

	if len(comments) != len(links) :
		print("Error in fbx : Not the same number of comments and connections")

	if verbose : print("Writing to file…")
	with open(filename+".xml", "w", encoding="utf8") as outputfile :
		if verbose : print("prettifying… (Can take a while for big files)")
		stringout = tools.prettifyXml(etree.tostring(root).decode())
		if verbose : print("writing…")
		outputfile.write(stringout)

	if verbose : print("End of builder_fromfbx for now")
