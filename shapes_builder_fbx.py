import os
import tools
import xml.etree.ElementTree as etree

def build(root, geometries, materials_ids, links_simple, links_revert, verbose = False, debug = False):
	if verbose : print("shapes_builder_fbx launched")
	if not os.path.exists("meshes") :
		os.makedirs("meshes")
	# Go through all geometry in the scene
	# TODO referençable shapes instead, what matters is «models»
	comment = etree.Comment("Shapes.")
	root.append(comment)

	geometries_id = []

	for geometry in geometries :

		only_triangles = True
		id, type, obj = geometry.get("value").replace("::","").split(", ")
		if obj != "Mesh" : print("Unknown Geometry obj : "+obj+" (id="+id+")")

		properties = tools.getProperties(geometry)
		linked_materials = links_revert[id] if id in links_revert else [] # Get the model(s) containing this geometry (Only the models reference materials)
		if len(linked_materials) == 1 :
			linked_materials = links_simple[linked_materials[0]]
		else :
			print("Multiple models containing same geometry ???")
			linked_materials = []
		linked_materials = [link for link in linked_materials if link in materials_ids] #Only keep ids of materials
		# I think that the index for materials is based on the order they appear in the file
		# Maybe not, but i see no other info in the fbx to know that.

		nb_polygons = int(geometry.find("PolygonVertexIndex").get("value").replace("*",""))
		if nb_polygons % 3 != 0 : only_triangles = False
		nb_polygons = int(nb_polygons/3)
		polygons_vertex_index_unformatted = geometry.find("PolygonVertexIndex").find("a").text.split(",")

		for i in range(len(polygons_vertex_index_unformatted)) :
			if i % 3 == 2 and not polygons_vertex_index_unformatted[i].startswith("-") : only_triangles = False

		polygons_vertex_index_temp = list(map(int, geometry.find("PolygonVertexIndex").find("a").text.split(",")))

		if 3*nb_polygons != len(polygons_vertex_index_temp) : only_triangles = False

		vertices_temp = geometry.find("Vertices").find("a").text.split(",")
		normals_temp = geometry.find("LayerElementNormal").find("Normals").find("a").text.split(",")

		if not only_triangles :
			print("ONLY 3-sided polygons accepted for now ! id in the fbx : "+id)
		else :
			geometries_id.append(id)
			vertices, normals = [], []
			for i in range(len(polygons_vertex_index_temp)) :
				index = polygons_vertex_index_temp[i]
				if index < 0 :
					# This is strange, but it works. The FBX has this strange property…
					# The - before an index means both that this is the end of this polygon and that you have to substract 1 to the index.
					# I have no idea who though it was a good idea, i had a hard time figuring out how to decipher this.
					index=-index-1
				vertices.append(" ".join(vertices_temp[3*index:3*index+3]))
				normals.append(" ".join(normals_temp[3*i:3*i+3]))

			polygons_vertex_index = []
			for i in range(len(polygons_vertex_index_temp)) :
				polygons_vertex_index.append(str(i))

			materials = geometry.find("LayerElementMaterial")
			if materials != None :
				materials = list(map(int, materials.find("Materials").find("a").text.split(",")))
			if materials == None or len(materials)<=1 :
				materials = [0 for i in range(nb_polygons)]
			max_material = max(materials)

			getLayerUv = geometry.find("LayerElementUV")
			uv = []
			if getLayerUv == None :
				if verbose : print("Empty layeruv in "+id)
			else :
				layerUv = getLayerUv
				uvs = layerUv.find("UV").find("a").text.split(",")
				uvsindex = layerUv.find("UVIndex").find("a").text.split(",")
				for i in range(len(uvsindex)) :
					index = int(uvsindex[i])
					uv.append(" ".join(uvs[2*index:2*index+2]))


			vertices_out = []
			normals_out  = []
			uv_out       = []
			# Initialize
			for i in range(max_material+1) :
				vertices_out.append([])
				normals_out.append([])
				uv_out.append([])

			for i in range(nb_polygons) :
				vertices_out[materials[i]].extend(vertices[3*i:3*i+3])
				normals_out[materials[i]].extend(normals[3*i:3*i+3])
				uv_out[materials[i]].extend(uv[3*i:3*i+3])

			# The shapegroup will contain all meshes with different materials, and allow instanciation
			shapegroup = etree.SubElement(root, "shape")
			shapegroup.set("type", "shapegroup")
			shapegroup.set("id", id)

			for i in range(max_material+1) :


				output = open("meshes/"+id+"_"+str(i)+".ply", "w")
				output.write("ply\n")
				output.write("format ascii 1.0\n")
				output.write("element vertex " + str(len(vertices_out[i]))+"\n")
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
				output.write("element face "+str(int(len(vertices_out[i])/3))+"\n")
				output.write("property list uint8 int32 vertex_indices\n")
				output.write("end_header\n")

				for j in range(len(vertices_out[i])) :
					output.write(vertices_out[i][j]+" ")
					output.write(normals_out[i][j]+" ")
					output.write(uv_out[i][j]+"\n")
				for j in range(int(len(vertices_out[i])/3)) :
					output.write("3 "+str(3*j)+" "+str(3*j+1)+" "+str(3*j+2)+"\n")

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
