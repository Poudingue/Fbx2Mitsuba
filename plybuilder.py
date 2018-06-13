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

	mesh =  geomobject.getElementsByTagName("MESH")[0]

	# All vertices needed. To have the right per-vertex normals, we'll need 3 times more in the final file
	mesh_vertices_list = mesh.getElementsByTagName("MESH_VERTEX_LIST")[0].getElementsByTagName("MESH_VERTEX")
	# Contains triplets of vertex ids, and vertex normals.
	mesh_normals_list  = mesh.getElementsByTagName("MESH_NORMALS")[0].getElementsByTagName("MESH_FACENORMAL")

	output_vertices=[]
	output_faces=[]

	for mesh_normal in mesh_normals_list :
		vertices = mesh_normal.getElementsByTagName("MESH_VERTEXNORMAL")
		if len(vertices)!=3 :
			print("NOT A 3-SIDED POLYGON : "+str(len(vertices)))
		for vertex in vertices :
			idvertex = int(vertex.getAttribute("id"))
			if str(idvertex) != mesh_vertices_list[idvertex].getAttribute("id"):
				print("MESH_VERTICES NOT IN THE ORDER OF ID")
			vertexcoords = mesh_vertices_list[idvertex].getAttribute("value")
			vertexnormals = vertex.getAttribute("value")
			output_vertices.append(vertexcoords+" "+vertexnormals)

	if len(output_vertices)%3!=0:
		print("Number of vertices not a multiple of 3")
	for i in range(int(len(output_vertices)/3)) :
		output_faces.append("3 "+str(3*i)+" "+str(3*i+1)+" "+str(3*i+2))

	output = open("meshes/"+name+".ply", "w")
	output.write("ply\n")
	output.write("format ascii 1.0\n")
	output.write("element vertex "+str(len(output_vertices))+"\n")
	output.write("property float32 x\n")
	output.write("property float32 y\n")
	output.write("property float32 z\n")
	output.write("property float32 nx\n")
	output.write("property float32 ny\n")
	output.write("property float32 nz\n")
	output.write("element face "+str(len(output_faces))+"\n")
	output.write("property list uint8 int32 vertex_indices\n")
	output.write("end_header\n")

	for vertex in output_vertices :
		output.write(vertex+"\n")

	for face in output_faces :
		output.write(face+"\n")

	output.close()
