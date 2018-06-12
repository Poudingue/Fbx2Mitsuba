import os
import time
import xml.etree.cElementTree as etree
import xml.dom.minidom as dom

inputfile = open("simplecubease.xml", "r")

inputdata = dom.parse(inputfile)

if not os.path.exists("meshes") :
	os.makedirs("meshes")

for geomobject in inputdata.getElementsByTagName("GEOMOBJECT") :
	name =  geomobject.getAttribute("NODE_NAME")

	mesh =  geomobject.getElementsByTagName("MESH")[0]#There should be only one
	nb_vertices = int(mesh.getAttribute("MESH_NUMVERTEX"))
	nb_faces    = int(mesh.getAttribute("MESH_NUMFACES" ))

	mesh_vertices_list = mesh.getElementsByTagName("MESH_VERTEX_LIST")[0].getElementsByTagName("MESH_VERTEX")
	mesh_faces_list    = mesh.getElementsByTagName("MESH_FACE_LIST")[0].getElementsByTagName("MESH_FACE")
	mesh_normals_list  = mesh.getElementsByTagName("MESH_NORMALS")[0].getElementsByTagName("MESH_FACENORMAL")

	output = open("meshes/"+name+".ply", "w")
	output.write("ply\n")
	output.write("format ascii 1.0\n")
	output.write("element vertex "+str(nb_vertices)+"\n")
	output.write("property float32 x\n")
	output.write("property float32 y\n")
	output.write("property float32 z\n")
	output.write("element face "+str(nb_faces)+"\n")
	output.write("property list uint8 int32 vertex_indices\n")
	output.write("property float32 nx\n")
	output.write("property float32 ny\n")
	output.write("property float32 nz\n")
	output.write("end_header\n")

	for i in range(nb_vertices) :
		if(mesh_vertices_list[i].getAttribute("id")==str(i)):
			output.write(mesh_vertices_list[i].getAttribute("value")+"\n")
		else :
			print("MESH_VERTICES IN THE WRONG ORDER : "+name)

	for i in range(nb_faces) :
		curr_face = mesh_faces_list[i]
		curr_normal = mesh_normals_list[i]
		if(curr_face.getAttribute("id")==str(i) and curr_normal.getAttribute("id")==str(i)):
			output.write("3 ")# Should be only 3 vertex faces with 3dsmax format
			output.write(curr_face.getAttribute("A")+" ")
			output.write(curr_face.getAttribute("B")+" ")
			output.write(curr_face.getAttribute("C")+" ")
			output.write(curr_normal.getAttribute("value")+"\n")

		else :
			print("MESH_FACES or MESH_NORMALS IN THE WRONG ORDER : "+name)

	output.close()
