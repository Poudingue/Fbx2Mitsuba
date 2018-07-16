import os
import xml.etree.cElementTree as etree

def extract(fbxtree, verbose=False, debug=False):
	print("fbx_extract launched")
	inputdata = fbxtree
	big_dictionnary = {}
	connections_list = inputdata.find("Connections")
	comments = connections_list.findall("comment")
	connections = connections_list.findall("C")

	if len(comments)!=len(connections) :
		print("comments and connections are not of the same length")
		exit(1)

	for i in range(len(comments)) :
		comment    = comments[i]
		connection = connections[i]

		objects = str(comment.text).split(", ")
		ids     = str(connection.text).split(",")
		object1, object2 = objects
		if object1.startswith("Template"):
			object1type, obj1num, obj1name = object1.split(" - ")
			object1name = obj1name+"_"+obj1num
		else :
			object1type, object1name = object1.split("::")
		object2type, object2name = object2.split("::")

		# Not sure what «something» is supposed to be yet.
		# But when it's OO, there are 3 arguments, 4 else.
		if ids[0] == "OO":
			complementary = "None"
			something, id1, id2 = ids
		else :
			something, id1, id2, complementary = ids

		if object1name=="":
			object1name=object2name
		if object1name not in ["T", "R", "S"] :
			object1name = object1type +"_"+ object1name.replace(" ","_")
			id_in_dict1 = big_dictionnary.get(object1name)
			if id_in_dict1!=None and id_in_dict1!=id1 :
				if verbose : print(object1name+" already in dict with id : "+ id1 +" vs "+id_in_dict1)
			else : big_dictionnary[object1name]=id1

		object2name = object2type + "_" + object2name.replace(" ","_")
		id_in_dict2 = big_dictionnary.get(object2name)
		if id_in_dict2!=None and id_in_dict2 != id2 :
			print(object2name +" already in dict with id : "+ id2 +" vs "+id_in_dict2)
		else : big_dictionnary[object2name]=id2

	objects_list = inputdata.find("Objects")
	geometry_list = objects_list.findall("Geometry")
	geometry_temp_dict = {}
	for geometry in geometry_list :

		id = geometry.get("value").split(",")[0]
		geometry_temp_dict[id]=geometry
	# Xml structure of the correct object can be accessed directly
	GeometryInfos = {}

	for stuff in big_dictionnary :
		if stuff.startswith("Geometry") :
			GeometryInfos[stuff]=geometry_temp_dict[big_dictionnary[stuff]]
		elif verbose : print("Unknown stuff : "+stuff)

	if not os.path.exists("fbxinfos") :
		os.makedirs("fbxinfos")
	for stuff in GeometryInfos :
		outputdata = GeometryInfos[stuff]
		# Replace uv+uvindex by simple uv list
		getLayerUv = outputdata.find("LayerElementUV")
		if getLayerUv == None :
			if verbose : print("Empty layeruv in "+stuff)
			uvout=""
		else :
			layerUv = getLayerUv
			uvs = layerUv.find("UV").find("a").text.split(",")
			uvsindex = layerUv.find("UVIndex").find("a").text.split(",")
			uvout=""
			for i in range(len(uvsindex)) :
				curr_index = int(uvsindex[i])
				uvout+=(uvs[2*curr_index]+" "+uvs[2*curr_index+1]+",")
		# Write in the correct file
		output_uv = open("fbxinfos/"+stuff+"_uv.txt", "w", encoding="utf8")
		output_uv.write(uvout)

		et = etree.ElementTree(GeometryInfos[stuff])
		et.write("fbxinfos/"+stuff+".xml", encoding="utf8")
