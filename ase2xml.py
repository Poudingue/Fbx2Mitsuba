import time
import re
import xml.etree.cElementTree as etree
import xml.dom.minidom as dom

inputfile = open("simplecube.ASE", "r")

root = etree.Element("root")
parents = []
current_elem = root

# Number of line before forcing a tag closing. Does nothing at -1
countdown_to_closing = -1

#The first line is "3DSMAX_ASCIIEXPORT	200",
#the 3 at the beginning would make it an incorrect xml file,
#so we just ignore this line
inputfile.readline()

line = inputfile.readline().strip().replace("\t", " ") # Always remove tabs
while line:
	print(str(countdown_to_closing))
	if countdown_to_closing==0 :
		current_elem = parents.pop()
	if countdown_to_closing >= 0 :
		countdown_to_closing -= 1


	# Regex for opening of new tag
	regopen = re.match("\*(([A-Z]|\_| |\d)*) \{", line)
	# Regex for setting up a value (or setting up a new material/vertex/other)
	regset = re.match("\*(([A-Z]|\_|\d)*)([ ]|[\t])*(.*)", line)

	#Line starting with * and ending with {, we create a new child while remembering our parents
	if regopen!=None :
		parents.append(current_elem)

		# Materials are written as "MATERIAL 3" or "SUBMATERIAL 3", Vertices as "MESH_VERTEX 0", "MESH_VERTEX 1", etc...
		# we just create different <material/>, but with an id

		regwrongspace = re.match("(SUBMATERIAL|MATERIAL) (\d+)", regopen[1])
		if regwrongspace!=None :
			current_elem = etree.SubElement(current_elem, (regwrongspace[1]))
			current_elem.set("id", regwrongspace[2])
		else :
			current_elem = etree.SubElement(current_elem, regopen[1])

	#Line starting with * but not ending with {, we set the correct property
	elif  regset!=None :
		# This case if for example for an element of a vertex list, we should create a new tag or only the last value will be kept
		regelementoflist = re.match(" *\*(MESH_(VERTEX|FACE|TVERT|VERTEXNORMAL|FACENORMAL)) *(\d+)(.*)", line)
		if regelementoflist!=None :
			parents.append(current_elem)
			current_elem = etree.SubElement(current_elem, regelementoflist[1])
			current_elem.set("id", regelementoflist[3])
			current_elem.set("value", regelementoflist[4])

		# FACENORMAL should be a new tag
			if regelementoflist[1]=="MESH_FACENORMAL" :
				countdown_to_closing = 3
				# FACENORMAL is followed by 3 lines that should be countained in it
				#So we delay the closing of the tag and going back to the parent
			else :
				current_elem = parents.pop()

		else :
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
tree.write("simplecubease.xml")


xmlstr = dom.parse("simplecubease.xml")

# print(xmlstr.toprettyxml())
outputfile = open("simplecubease.xml", "w")
outputfile.write(xmlstr.toprettyxml())

# time.sleep(1)
