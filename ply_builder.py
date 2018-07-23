import os
import xml.etree.ElementTree as etree

def build(asetree, verbose = False, debug = False):
	if verbose : print("plybuilder launched")
	if not os.path.exists("meshes") :
		os.makedirs("meshes")
	if not os.path.exists("materials") :
		os.makedirs("materials")

	materials = asetree.find("MATERIAL_LIST").findall("MATERIAL")

	# Go through all geometry in the scene
	for geomobject in asetree.findall("GEOMOBJECT") :
		name = geomobject.get("NODE_NAME")
		mesh = geomobject.find("MESH")

		# All vertices needed. To have the right per-vertex normals, we'll need 3 times more in the final file
		mesh_vertices_list = mesh.find("MESH_VERTEX_LIST").findall("MESH_VERTEX")
		# Contains triplets, but also material references.
		mesh_faces_list    = mesh.find("MESH_FACE_LIST").findall("MESH_FACE")
		# Contains triplets of vertex ids, and vertex normals.
		mesh_normals_list  = mesh.find("MESH_NORMALS").findall("MESH_FACENORMAL")
		# Get the uv from the fbx file
		input_uv = open("fbxinfos/Geometry_"+ name +"_uv.txt", "r")
		mesh_uv_list = input_uv.readline().split(",")

		# Materials of the scene
		list_materials=[]
		out_materials = etree.Element("materials")

		curr_material_id = geomobject.get("MATERIAL_REF")
		if curr_material_id == None :
			# if verbose : print("Object "+name+" has no material assigned to it. Using wireframe color")
			# curr_diffuse = geomobject.get("WIREFRAME_COLOR")
			if verbose : print("Object "+name+" has no material assigned to it. Using RED diffuse.")
			curr_diffuse = "1 0 0"
			curr_export_material = etree.SubElement(out_materials, "bsdf")
			# Default material : phong. Blinn not supported by Mitsuba.
			curr_export_material.set("type", "diffuse")
			# curr_export_material.set("id", name+"_material_0")
			diffuse = etree.SubElement(curr_export_material, "spectrum")
			diffuse.set("name", "diffuseReflectance")
			diffuse.set("value", curr_diffuse)

			submaterials = []
		else:
			# Get the correct material
			curr_material = materials[int(curr_material_id)]
			if curr_material.get("id")!=curr_material_id :
				print("Materials not ordered by id for object "+name)
				exit(0)
			submaterials = curr_material.findall("SUBMATERIAL")

		one_material_only = submaterials==[]


		# Get nb of different submaterials in a single object : Each material will have its own «sub-object»
		for mesh_face in mesh_faces_list :
			mat_id = int(mesh_face.get("MESH_MTLID"))
			if mat_id not in list_materials :
				list_materials.append(mat_id)

		if one_material_only and curr_material_id!=None :
			submaterials.append(materials[int(curr_material_id)])

		for material in submaterials:
			mat_id = material.get("id")
			curr_export_material = etree.SubElement(out_materials, "bsdf")
			# Default material : phong. Blinn not supported by Mitsuba.
			curr_export_material.set("type", "phong")
			# curr_export_material.set("id", name+"_material_"+mat_id)
			diffuse_texture = material.findall("MAP_DIFFUSE")
			texture_present = diffuse_texture!=[]
			if texture_present :
				bitmap_diffuse_texture = diffuse_texture[0].get("BITMAP")
			curr_diffuse = material.get("MATERIAL_DIFFUSE")
			specular_level = float(material.get("MATERIAL_SHINESTRENGTH"))
			specular_color = material.get("MATERIAL_SPECULAR").split()
			for component in specular_color :
				component = str(specular_level*float(component))
			# Encoded in the 0-1 range, have to convert to 0-100
			glossiness = 100*float(material.get("MATERIAL_SHINE"))
			exponent = etree.SubElement(curr_export_material, "float")
			exponent.set("name", "exponent")
			exponent.set("value", str(glossiness))
			diffuse = etree.SubElement(curr_export_material, "texture" if texture_present else "spectrum")
			diffuse.set("name", "diffuseReflectance")
			diffuse.set("type" if texture_present else "value", "bitmap" if texture_present else curr_diffuse)
			if texture_present :
				texture_reference = etree.SubElement(diffuse, "string")
				texture_reference.set("name", "filename")
				texture_reference.set("value", bitmap_diffuse_texture)
			specular = etree.SubElement(curr_export_material, "spectrum")
			specular.set("name", "specularReflectance")
			specular.set("value", specular_color[0]+" "+specular_color[1]+" "+specular_color[2])

		# if submaterials != []:
		# 	curr_bsdf = etree.SubElement(out_materials[mat_id], "bsdf")
		for material in out_materials :
			id_material = material.get("id")
			if one_material_only :
				id_material=name+"_material_0"
			materialtree = etree.ElementTree(material)
			materialtree.write("materials/"+str(id_material)+".xml")

		# To store the place where the ids are in the materials_list
		material_place = [-1]*(1+max(list_materials))# There can be ids higher that the nb of materials. -1 for errors
		for i in range(len(list_materials)) :
			material_place[list_materials[i]]=i

		output_vertices_list = []
		output_faces_list    = []
		for i in range(len(list_materials)) :
			output_vertices_list.append([])
			output_faces_list.append([])

		if len(mesh_faces_list)!=len(mesh_normals_list) :
			print("Not same number of faces and vertex triplets in object "+name)

		idforuv = 0
		print(name+" : "+str(len(mesh_faces_list))+" faces.")
		for i in range(len(mesh_faces_list)) :
			mesh_face   = mesh_faces_list[i]
			mesh_normal = mesh_normals_list[i]
			if not (mesh_face.get("id") == mesh_normal.get("id") and str(i) == mesh_normal.get("id")):
				print("faces not in id order in object "+name)

			vertices = mesh_normal.findall("MESH_VERTEXNORMAL")
			mtlid = int(mesh_face.get("MESH_MTLID"))
			mtl_place = material_place[mtlid]

			if len(vertices)!=3 : print("not a 3-sided polygon : "+str(len(vertices)))
			curr_output_vertices=output_vertices_list[mtl_place]

			for vertex in vertices :
				idvertex = int(vertex.get("id"))
				if str(idvertex) != mesh_vertices_list[idvertex].get("id") : print("MESH_VERTICES not in the order of id")
				vertexcoords = mesh_vertices_list[idvertex].get("value")
				vertexnormals = vertex.get("value")
				# TODO voir comment accéder à l'uvmap proprement
				if(idforuv>=len(mesh_uv_list)-1):
					uvmap = "0 0"
				else:
					uvmap = mesh_uv_list[idforuv]
				idforuv+=1
				curr_output_vertices.append(vertexcoords+" "+vertexnormals+" "+uvmap)

		for i in range(len(output_vertices_list)) :
			output_vertices = output_vertices_list[i]
			output_faces = output_faces_list[i]
			nb_vertices = len(output_vertices)
			if nb_vertices%3 != 0 : print("Number of vertices not a multiple of 3")
			for j in range(int(nb_vertices/3)) :
				output_faces.append("3 "+str(3*j)+" "+str(3*j+1)+" "+str(3*j+2))

		for i in range(len(list_materials)):
			matplace = material_place[i]
			output = open("meshes/"+name+"_"+str(i)+".ply", "w")
			output.write("ply\n")
			output.write("format ascii 1.0\n")
			output.write("element vertex "+str(len(output_vertices_list[matplace]))+"\n")
			output.write("property float32 x\n")
			output.write("property float32 y\n")
			output.write("property float32 z\n")
			output.write("property float32 nx\n")
			output.write("property float32 ny\n")
			output.write("property float32 nz\n")
			output.write("property float32 u\n")
			output.write("property float32 v\n")
			output.write("element face "+str(len(output_faces_list[matplace]))+"\n")
			output.write("property list uint8 int32 vertex_indices\n")
			output.write("end_header\n")

			for vertex in output_vertices_list[material_place[i]] :
				output.write(vertex+"\n")

			for face in output_faces_list[material_place[i]][:-1] :
				output.write(face+"\n")
			output.write(output_faces_list[material_place[i]][-1])
