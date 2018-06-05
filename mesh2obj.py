import time
inputfile = open("justcubemesh.ASE", "r")
outputfile = open("finalmesh.obj", "w")
# Depth is the number of opening and non closed yet brackets.
depth = 1

def handleVertex(line):
	print("\t\tvertexHandled : "+line)

def handleFace(line):
	print("\t\tfaceHandled : "+line)

def handleVertices():
	global depth
	print("i am handleVertices")
	line =inputfile.readline().strip()
	while line:
		if line.startswith("*MESH_VERTEX"):
			handleVertex(line)
		elif line.startswith("*"):
			print(line+" not implemented yet")
		if line.endswith("}"):
			depth-=1
			break
		line =inputfile.readline().strip()
	print("handleVertices ended\n")

def handleFaces():
	global depth
	print("i am handleFaces")
	line =inputfile.readline().strip()
	while line:
		if line.startswith("*MESH_FACE"):
			handleFace(line)
		elif line.startswith("*"):
			print(line+" not implemented yet")
		if line.endswith("}"):
			depth-=1
			break
		line =inputfile.readline().strip()
	print("handleFaces ended\n")

line = inputfile.readline().strip()
while line:

	# Keeping track of depth
	if line.endswith("}"):
		depth -= 1
	elif line.endswith("{"):
		depth += 1


	line = inputfile.readline().strip()
	if line.startswith("*MESH_VERTEX_LIST"):
		handleVertices()
	elif line.startswith("*MESH_FACE_LIST"):
		handleFaces()
	elif line.startswith("*"):
		print(line+" not implemented yet\n")


if depth != 0:
	print("error, "+str(depth)+" brackets left unclosed")
print("bye bye !")
time.sleep(1)
