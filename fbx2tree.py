import re
import tools
import config
import xml.etree.ElementTree as etree

def transform() :
	filename = config.filename
	verbose  = config.verbose
	debug    = config.debug

	if verbose : print("fbx2tree launched…")
	root = etree.Element("root")
	parents = []
	current_elem = root
	inputfile = open(filename+".fbx", encoding="utf8")
	if verbose : print("file openened")

	for line in inputfile :
		line = line.replace("\"","")
		# print(line)
		# Comments in the fbx can give useful informations
		reg_comment = re.match(";(.*)", line.strip())
		#
		reg_opening = re.match("([A-Za-z0-9_]+):(.*) *{", line.strip())
		reg_info = re.match("([A-Za-z0-9_]+): *(.*)", line.strip())
		if "}" in line :
			current_elem = parents.pop()
		elif len(line.strip()) == 0 :
			pass
		elif reg_comment!=None :
			comment = etree.SubElement(current_elem, "comment")
			comment.text = reg_comment[1]
		elif reg_opening!=None :
			parents.append(current_elem)
			current_elem = etree.SubElement(current_elem, reg_opening[1].replace(" ","").replace(":",""))
			current_elem.set("value",reg_opening[2].strip())
		elif reg_info!=None :
			moretext = ""
			if reg_info[2].endswith(",") :
				onemoreline = inputfile.readline().strip()
				if "}" in onemoreline :
					current_elem = parents.pop()
				else :
					moretext+=onemoreline
			while moretext.endswith(",") :
				onemoreline = inputfile.readline().strip()
				if "}" in onemoreline :
					current_elem = parents.pop()
				else :
					moretext+=onemoreline
			elem = etree.SubElement(current_elem, reg_info[1])
			elem.text = reg_info[2] + moretext
		else :
			print("unknown : "+line)
			stuff = etree.SubElement(current_elem, "stuff")
			stuff.text = line
	inputfile.close()

	if parents != [] :
		print("PARENTS LIST NOT EMPTY")
		print(parents)
		exit(1)

	if verbose : print ("Building tree")
	tree = etree.ElementTree(root)

	if debug :
		if verbose : print("writing file")
		with open(filename+"_fbx.xml", "w", encoding="utf8") as outputfile :
			if verbose : print("prettifying… (Can take a while for big files)")
			stringout = etree.tostring(root).decode()
			pretty = tools.prettifyXml(stringout)
			if verbose : print("writing…")
			outputfile.write(pretty)
	if verbose : print("fbx2tree ended")
	return tree
