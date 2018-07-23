import xml.etree.ElementTree as etree

def build(geometries, verbose = False, debug = False):
	if verbose : print("plybuilder_fbx launched")

	# Go through all geometry in the scene
	for geometry in geometries :
		id, type, obj = geometry.get("value").replace("::","").split(", ")
		if obj != "Mesh" :
			print("Unknown Geometry obj : "+obj+" (id="+id+")")

		vertices_list = geometry.find("Vertices").find("a").text.split(",")
		polygons_vertex_index = []
		temp_poly_list = geometry.find("PolygonVertexIndex").find("a").text.split(",")
		if len(temp_poly_list)%3 != 0 :
			print("Polygons with more than 3 vertices unsupported in object "+id)
		for i in range(int(len(temp_poly_list)/3)) :
			if temp_poly_list[3*i+2].startswith("-") :
				polygons_vertex_index += (temp_poly_list[3*i]+" "+temp_poly_list[3*i+1]+" "+temp_poly_list[3*i+2].replace("-", ""))
			else :
				print("Polygons with more than 3 vertices unsupported in object "+id)

		normals_list = geometry.find("LayerElementNormal").find("Normals").find("a").text.split(",")
		material_list= geometry.find("LayerElementMaterial")
		if material_list!=None :
			material_list = material_list.find("Materials").find("a").text.split(",")
		else :
			material_list = [""]
			if verbose : print("Object "+id+" doesn't have multiple materials. Exporting only one mesh.")

		getLayerUv = geometry.find("LayerElementUV")
		uvout = []
		if getLayerUv == None :
			if verbose : print("Empty layeruv in "+id)
		else :
			layerUv = getLayerUv
			uvs = layerUv.find("UV").find("a").text.split(",")
			uvsindex = layerUv.find("UVIndex").find("a").text.split(",")
			for index in uvsindex :
				curr_index = int(index)
				uvout.append(uvs[2*curr_index]+" "+uvs[2*curr_index+1]+",")

		for i in material_list :
			output = open("meshes/"+id+"_"+str(i)+".ply", "w")
			output.write("ply\n")
			output.write("format ascii 1.0\n")
			output.write("element vertex "+str(len(output_vertices_list[i]))+"\n")
			output.write("property float32 x\n")
			output.write("property float32 y\n")
			output.write("property float32 z\n")
			output.write("property float32 nx\n")
			output.write("property float32 ny\n")
			output.write("property float32 nz\n")
			output.write("property float32 u\n")
			output.write("property float32 v\n")
			output.write("element face "+str(len(output_faces_list[i]))+"\n")
			output.write("property list uint8 int32 vertex_indices\n")
			output.write("end_header\n")

			for vertex in output_vertices_list[material_place[i]] :
				output.write(vertex+"\n")

			for face in output_faces_list[material_place[i]][:-1] :
				output.write(face+"\n")
			output.write(output_faces_list[material_place[i]][-1])
