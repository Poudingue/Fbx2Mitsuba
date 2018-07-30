import os
import tools
import xml.etree.ElementTree as etree

# allows extraction of correct data even with indexes and all the stuff
"""
def getValues(layerelement, nb_vertices, datatype) :
	mapping_type = layerelement.find("MappingInformationType").text
	reference_type = layerelement.find("ReferenceInformationType").text
	if datatype == "normals" :
		inputdata = layerelement.find("Normals").find("a").text.split(",")
	elif datatype == "uv" :
		inputdata = layerelement.find("UV").find("a").text.split(",")
	else :
		print("Unknown type of layer : "+datatype)
	outdata = []
	if reference_type == "IndexToDirect" :
		index = layerelement.find("UV")

		for i in range(nb_vertices) :
			index = i else
			outdata.append(" ".join(uvs[2*i:2*i+2]))
	elif reference_type == "Direct" :
		uvsindex = layeruv.find("UVIndex").find("a").text.split(",")
		for i in range(len(uvsindex)) :
			index = int(uvsindex[i])
			outdata.append(" ".join(uvs[2*index:2*index+2]))
"""


def build(root, geometries, materials_ids, links_simple, links_revert, verbose = False, debug = False):
	if verbose : print("shapes_builder_fbx launched")
	if not os.path.exists("meshes") :
		os.makedirs("meshes")
	# Go through all geometry in the scene
	# TODO referençable shapes instead, what matters is «models»
	comment = etree.Comment("Shapes.")
	root.append(comment)

	geometries_id = []

	# Only keep geometries with polygonvertex
	geometries = [geometry for geometry in geometries if geometry.find("PolygonVertexIndex") != None ]

	for geometry in geometries :

		id, type, obj = geometry.get("value").replace("::","").split(", ")
		if obj != "Mesh" : print("Unknown Geometry obj : "+obj+" (id="+id+")")
		geometries_id.append(id)

		properties = tools.getProperties(geometry)
		linked_materials = links_revert[id] if id in links_revert else [] # Get the model(s) containing this geometry (Only the models reference materials)
		if len(linked_materials) == 1 :
			linked_materials = links_simple[linked_materials[0]]
		else :
			print("Multiple models containing geometry "+id+" ???")
			linked_materials = []
		linked_materials = [link for link in linked_materials if link in materials_ids] #Only keep ids of materials
		# I think that the index for materials is based on the order they appear in the file
		# Maybe not, but i see no other info in the fbx to know that.

		vertices_data = geometry.find("Vertices")
		nb_vertices = int(vertices_data.get("value").replace("*",""))

		polygons_data = geometry.find("PolygonVertexIndex")
		nb_poly_ind = int(polygons_data.get("value").replace("*",""))

		edges_data    = geometry.find("Edges")
		nb_edges    = int(   edges_data.get("value").replace("*",""))

		normal_layer  = geometry.find("LayerElementNormal")
		if normal_layer != None :
			normals_data  = normal_layer.find("Normals")
			normalsW_data = normal_layer.find("NormalsW")
			nb_normals  = int( normals_data.get("value").replace("*",""))
			nb_normalsW = int(normalsW_data.get("value").replace("*",""))

		uv_layer      = geometry.find("LayerElementUV")
		if uv_layer != None :
			uv_data       = uv_layer.find("UV")
			uv_index_data = uv_layer.find("UVIndex")
			nb_uv_data  = int(      uv_data.get("value").replace("*",""))
			nb_uv_index = int(uv_index_data.get("value").replace("*",""))

		material_layer= geometry.find("LayerElementMaterial")
		if material_layer != None :
			material_data = list(map(int, material_layer.find("Materials").find("a").text.split(",")))
			if material_layer.find("MappingInformationType").text == "AllSame" :
				material_data = nb_poly_ind * [material_data[0]]



		vertices_in =              vertices_data.find("a").text.split(",")
		polygons_in = list(map(int,polygons_data.find("a").text.split(",")))
		edges_in    =                 edges_data.find("a").text.split(",")
		normals_in  =               normals_data.find("a").text.split(",")
		normalsW_in =              normalsW_data.find("a").text.split(",")
		uv_in       =                    uv_data.find("a").text.split(",")
		uv_index_in = list(map(int,uv_index_data.find("a").text.split(",")))


		vertices, polygon_vertex_index, normals, uv = [], [], [], []

		if nb_vertices % 3 != 0 :
			print("Points values not a multiple of 3 !")
		for i in range(int(nb_vertices/3)) :
			vertices.append(vertices_in[3*i:3*i+3])


		curr_vertex = []
		for index in polygons_in :
			if index < 0 :
				curr_vertex.append(-index-1)
				polygon_vertex_index.append(curr_vertex)
				curr_vertex = []
			else :
				curr_vertex.append(index)
		nb_polygons = len(polygon_vertex_index)

		if normal_layer != None :
			normal_type = normal_layer.find("ReferenceInformationType").text
			if normal_type == "Direct" :
				for i in range(int(nb_normals/3)) :
					normals.append(normals_in[3*i:3*i+3])
			elif normal_type == "IndexToDirect" :
				# TODO
				print("NORMAL INDEXTODIRECT TO DO")
			else :
				print("Unknown ReferenceInformationType for normal in obj "+id)
		else :
			print("NO NORMALS for object with id "+id)

		if uv_layer != None :
			uv_type = uv_layer.find("ReferenceInformationType").text
			if uv_type == "Direct" :
				for i in range(int(nb_uv_data/2)) :
					uv.append(uv_in[2*i:2*i+2])
			elif uv_type == "IndexToDirect" :
				for i in range(int(nb_uv_index)) :
					index = uv_index_in[i]
					uv.append(uv_in[2*index:2*index+2])
			else :
				print("Unknown ReferenceInformationType for uv in obj "+id)
				uv = ["0 0"]*nb_poly_ind
		else :
			if verbose : print("No uv for object with id "+id+". Using default of 0, 0")
			uv = ["0 0"]*nb_poly_ind


		materials = geometry.find("LayerElementMaterial")
		if materials != None :
			materials = list(map(int, materials.find("Materials").find("a").text.split(",")))
		if materials == None or len(materials)<=1 :
			materials = [0 for i in range(nb_polygons)]
		max_material = max(materials)

		# The shapegroup will contain all meshes with different materials, and allow instanciation
		shapegroup = etree.SubElement(root, "shape")
		shapegroup.set("type", "shapegroup")
		shapegroup.set("id", id)

		# Initialize
		for i in range(max_material+1) :

			vertex_text = []
			poly_index  = []
			total_index = 0
			curr_polygon_vertex_num = 0

			for j in range(len(polygon_vertex_index)) :
				vertex_indexes = polygon_vertex_index[j]
				curr_poly_index = []
				for k in range(len(vertex_indexes)) :

					# Only keep polygons with the current material
					if material_layer == None or material_data[j] == i :
						curr_poly_index.append(str(total_index))
						total_index += 1
						vertex_index = vertex_indexes[k]
						curr_vertex_text  = " ".join(vertices[vertex_index]) +" "
						curr_vertex_text += " ".join( normals[curr_polygon_vertex_num]) +" "
						curr_vertex_text += " ".join(      uv[vertex_index])
						vertex_text.append(curr_vertex_text)
					curr_polygon_vertex_num += 1

				if len(curr_poly_index) > 3 :
					for k in range(len(curr_poly_index)-2) :
						curr_poly = [curr_poly_index[0]]+curr_poly_index[k+1:k+3]
						poly_index.append(curr_poly)
				elif len(curr_poly_index) > 0 :
					poly_index.append(curr_poly_index)


			output = open("meshes/"+id+"_"+str(i)+".ply", "w")
			output.write("ply\n")
			output.write("format ascii 1.0\n")
			output.write("element vertex " + str(len(vertex_text))+"\n")
			output.write(
"""property float32 x
property float32 y
property float32 z
property float32 nx
property float32 ny
property float32 nz
property float32 u
property float32 v
""")
			output.write("element face "+str(len(poly_index))+"\n")
			output.write("property list uint8 int32 vertex_indices\n")
			output.write("end_header\n")

			for vert in vertex_text :
				output.write(vert+"\n")

			for poly in poly_index : # Only triangles
				output.write("3 "+" ".join(poly)+"\n")

			shape = etree.SubElement(shapegroup, "shape")
			shape.set("type", "ply")

			importshape = etree.SubElement(shape, "string")
			importshape.set("name", "filename")
			importshape.set("value", "meshes/"+id+"_"+str(i)+".ply")

			try:
				curr_material = linked_materials[i]
				curr_bsdf = etree.SubElement(shape, "ref")
				curr_bsdf.set("name", "bsdf")
				curr_bsdf.set("id", curr_material)
			except IndexError:
				curr_material = 'null'
				print("No material found for object "+id+", index "+str(i))


	return geometries_id
