import os
import xml.etree.cElementTree as etree

def build(fbxtree, verbose = False, debug = False):
	if verbose : print("plybuilder launched")
	if not os.path.exists("meshes") :
		os.makedirs("meshes")
	if not os.path.exists("materials") :
		os.makedirs("materials")

	objects = fbxtree.find("Objects")

	models    = objects.findall("Model")
	geometry  = objects.findall("Geometry")
	materials = objects.findall("Material")
	nodes     = objects.findall("NodeAttribute") # Include cameras and lights
	videos    = objects.findall("Video") # Not sure about what it contains
	textures  = objects.findall("Texture")
	anim_c_n  = objects.findall("AnimationCurveNode")
	anim_c    = objects.findall("AnimationCurve")

	implem    = objects.find("Implementation")
	bind_table= objects.find("BindingTable")
	bind_oper = objects.find("BindingOperator")

	connections_list = fbxtree.find("Connections")
	# Comments contain infos about links between objects and their type
	comments = connections_list.findall("comment")
	links    = connections_list.findall("C")

	if len(comments) != len(links) :
		print("Error in fbx : Not the same number of comments and connections")

	if verbose : print("End of ply_builder_fromfbx for now")
