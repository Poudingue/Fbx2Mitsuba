import os
import tools
import xml.etree.ElementTree as etree

def build(root, geometries, models, verbose = False, debug = False):
	if verbose : print("plybuilder_fbx launched")
	if not os.path.exists("meshes") :
		os.makedirs("meshes")
	# Go through all geometry in the scene
	for geometry in geometries :
		id, type, obj = geometry.get("value").replace("::","").split(", ")
		if obj != "Mesh" : print("Unknown Geometry obj : "+obj+" (id="+id+")")

		properties = tools.getProperties(geometry)

		vertices = geometry.find("Vertices").find("a").text.split(",")

		nb_polygons = int(geometry.find("PolygonVertexIndex").get("value").replace("*",""))
		polygons_vertex_index = geometry.find("PolygonVertexIndex").find("a").text.replace("-","").split(",")
		if nb_polygons != len(polygons_vertex_index) : print("Error in obj "+id+", only 3-sided polygons supported.")

		normals = geometry.find("LayerElementNormal").find("Normals").find("a").text.split(",")

		materials = geometry.find("LayerElementMaterial")
		if materials != None :
			materials = list(map(int, materials.find("Materials").find("a").text.split(",")))
		else :
			materials = [0]*len(polygons_vertex_index)
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
				uv.append(" ".join(uvs[2*i:2*i+2]))

		vertices_out = []
		normals_out  = []
		uv_out       = []
		polygons_out = []
		# Initialize
		for i in range(max_material+1) :
			vertices_out.append([])
			normals_out.append([])
			uv_out.append([])
			polygons_out.append([])

		for i in range(len(materials)) :
			vertices_out[materials[i]].append(" ".join(vertices[3*i:3*i+3]))
			normals_out[materials[i]].append(" ".join(normals[3*i:3*i+3]))
			uv_out[materials[i]].append(" ".join(uv[2*i:2*i+2]))
			polygons_out[materials[i]].append(" ".join(polygons_vertex_index[3*i:3*i+3]))

		for i in range(max_material) :
			if i in materials :
				output = open("meshes/"+id+"_"+str(i)+".ply", "w")
				output.write("ply\n")
				output.write("format ascii 1.0\n")
				output.write("element vertex "+str(len(vertices_out[i]))+"\n")
				output.write("property float32 x\n")
				output.write("property float32 y\n")
				output.write("property float32 z\n")
				output.write("property float32 nx\n")
				output.write("property float32 ny\n")
				output.write("property float32 nz\n")
				output.write("property float32 u\n")
				output.write("property float32 v\n")
				output.write("element face "+str(len(polygons_out[i]))+"\n")
				output.write("property list uint8 int32 vertex_indices\n")
				output.write("end_header\n")

				for j in range(len(vertices_out[i])) :
					output.write(vertices_out[i][j]+" ")
					output.write(normals_out[i][j]+" ")
					output.write(uv_out[i][j]+"\n")

				for face in polygons_out[i] :
					output.write("3 "+face+"\n")
