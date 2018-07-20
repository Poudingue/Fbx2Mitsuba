import re
import tools
import xml.etree.cElementTree as etree

def transform(filename, verbose = False, debug = False):
	if verbose : print("ase2tree launched…")
	inputfile = open(filename+".ASE", "r")
	if verbose : print("file openened")
	root = etree.Element("root")
	parents = []
	current_elem = root

	# Number of line before forcing a tag closing. Does nothing at -1
	countdown_to_closing = -1

	for line in inputfile :
		line = line.strip().replace("\t", " ")# Always remove tabs
		if countdown_to_closing == 0 :
			current_elem = parents.pop()
		if countdown_to_closing >= 0 :
			countdown_to_closing -= 1

		# Regex for opening of new tag
		regopen = re.match("\*(([A-Z]|\_| |\d)*) \{", line)
		# Regex for setting up a value (or setting up a new material/vertex/other)
		regset = re.match("\*(([A-Z]|\_|\d)*)([ ]|[\t])*(.*)", line)
		# Regex for groups
		regroup= re.match("\*(GROUP \"(.*)\") \{", line)

		#Line starting with * and ending with {, we create a new child while remembering our parents
		if regopen != None :
			parents.append(current_elem)

			# Materials are written as "MATERIAL 3" or "SUBMATERIAL 3", Vertices as "MESH_VERTEX 0", "MESH_VERTEX 1", etc...
			# we just create different <material/>, but with an id
			regwrongspace = re.match("(SUBMATERIAL|MATERIAL|SHAPE_LINE) (\d+)", regopen[1])
			if regwrongspace != None :
				current_elem = etree.SubElement(current_elem, (regwrongspace[1]))
				current_elem.set("id", regwrongspace[2])
			else :
				current_elem = etree.SubElement(current_elem, regopen[1])
		elif regroup != None :
			parents.append(current_elem)
			current_elem = etree.SubElement(current_elem, ("GROUP_"+regroup[2]))
			if verbose : print("Group "+regroup[2]+" added")
		#Line starting with * but not ending with {, we set the correct property
		elif regset != None :
			# This case if for example for an element of a vertex list, we should create a new tag or only the last value will be kept
			regelementoflist = re.match(" *\*(MESH_(VERTEX|FACE|TVERT|VERTEXNORMAL|FACENORMAL)) *(\d+)(.*)", line)
			if regelementoflist != None :
				parents.append(current_elem)
				current_elem = etree.SubElement(current_elem, regelementoflist[1])
				current_elem.set("id", regelementoflist[3])
				# MESH_FACE has multiple value, a little formating to have a cleaner xml
				if regelementoflist[1] == "MESH_FACE" :
					parts = regelementoflist[4].split("*")
					parts2 = parts[0].replace(":"," ").split()
					current_elem.set("A", parts2[1])
					current_elem.set("B", parts2[3])
					current_elem.set("C", parts2[5])
					current_elem.set("AB", parts2[7])
					current_elem.set("BC", parts2[9])
					current_elem.set("CA", parts2[11])
					if(len(parts[1].split())>1) :
						current_elem.set("MESH_SMOOTHING",parts[1].split()[1])
					current_elem.set("MESH_MTLID",parts[2].split()[1])
				else:
					current_elem.set("value", regelementoflist[4].strip())

			# FACENORMAL should be a new tag
				if regelementoflist[1] == "MESH_FACENORMAL" :
					countdown_to_closing = 3
					# FACENORMAL is followed by 3 lines that should be countained in it
					#So we delay the closing of the tag and going back to the parent
				else :
					current_elem = parents.pop()
			else :
				current_elem.set(regset[1], regset[4].replace("\"","")) # Removing unwanted quotes
		# we go back to the parent element
		elif line=="}" :
			# debug print
			if parents==[]:
				print("NO PARENTS FOUND")
			else :
				current_elem = parents.pop()
		else :
			print("UNRECOGNIZED LINE : "+line)


	if parents != [] :
		print("PARENTS LIST NOT EMPTY")

	if verbose : print ("Building tree")
	tree = etree.ElementTree(root)

	if debug :
		if verbose : print("writing file")
		with open(filename+"_ase.xml", "w", encoding="utf8") as outputfile :
			if verbose : print("prettifying… (Can take a while for big files)")
			stringout = tools.prettifyXml(etree.tostring(root).decode())
			if verbose : print("writing…")
			outputfile.write(stringout)
	return tree
