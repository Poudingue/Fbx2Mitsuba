import time
import re
import xml.etree.cElementTree as etree
import xml.dom.minidom as dom

inputfile = open("simplecube.ASE", "r")

root = etree.Element("root")
parents = []
current_elem = root

#The first line is "3DSMAX_ASCIIEXPORT	200",
#the 3 at the beginning would make it an incorrect xml file,
#so we just ignore this line
inputfile.readline()

line = inputfile.readline().strip().replace("\t", " ") # Always remove tabs
while line:
	regopen = re.match("\*(([A-Z]|\_| |[0-9])*) \{", line)
	regset = re.match("\*(([A-Z]|\_|[0-9])*)([ ]|[\t])*(.*)", line)

	#Line starting with * and ending with {, we create a new child while remembering our parents
	if regopen!=None :
		parents.append(current_elem)

		# Materials are written as "MATERIAL 3" or "SUBMATERIAL 3", Vertices as "MESH_VERTEX 0", "MESH_VERTEX 1", etc...
		# we should write "MATERIAL_” or "SUBMATERIAL_3" to have a correct XML document
		regwrongspace = re.match("(.*MATERIAL|(MESH_(VERTEX|TFACE|FACE|TVERT|VERT|FACENORMAL|VERTEXNORMAL))) (\d)", regopen[1])
		if regwrongspace!=None :
			current_elem = etree.SubElement(current_elem, (regwrongspace[1]+"_"+regwrongspace[4]))
		else :
			current_elem = etree.SubElement(current_elem, regopen[1])

	#Line starting with * but not ending with {, we set the correct property
	elif  regset!=None :
		current_elem.set(regset[1], regset[4].replace("\"","")) # Removing unwanted quotes

	# we go back to the parent element
	elif line=="}" :
		# Debug print
		if parents==[]:
			print("NO PARENTS FOUND")
		else :
			current_elem = parents.pop()
	else :
		print("UNRECOGNIZED LINE : "+line)

	line = inputfile.readline().strip().replace("\t", " ") # Always remove tabs

if parents != [] :
	print("PARENTS LIST NOT EMPTY")

tree = etree.ElementTree(root)
tree.write("simplecube.xml")


xmlstr = dom.parse("simplecube.xml")

# print(xmlstr.toprettyxml())
outputfile = open("simplecube.xml", "w")
outputfile.write(xmlstr.toprettyxml())

time.sleep(1)
