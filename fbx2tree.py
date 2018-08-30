import re
import tools
import config
import xml.etree.ElementTree as etree

def transform() :
	"""
	This function generates an element tree from the FBX file
	"""
	filepath, filename, verbose, debug = config.filepath, config.filename, config.verbose, config.debug

	if verbose : print("fbx2tree launched…")
	root = etree.Element("root")
	parents = [] # Store a list of current parents

	current_elem = root
	inputfile = open(filepath+filename+".fbx", encoding="utf8")
	if verbose : print("file openened")

	for line in inputfile :
		line = line.replace("\"","").strip()
		reg_comment = re.match(";(.*)", line)					# This regex corresponds to comments
		reg_opening = re.match("([A-Za-z0-9_]+):(.*) *{", line) # This regex corresponds to a new child
		reg_info = re.match("([A-Za-z0-9_]+): *(.*)", line)		# This regex corresponds to infos for the current child

		if line.endswith("}") :									# This is the end of the current element, go back to the parent.
			current_elem = parents.pop()

		elif len(line.strip()) == 0 :							# Empty line, simply ignore
			pass

		elif reg_comment != None :								# Comment, just create an element named comment.
			comment      = etree.SubElement(current_elem, "comment")
			comment.text = reg_comment[1]

		elif reg_opening != None :								# New child, remember the parrent, and create the new child.
			parents.append(current_elem)
			current_elem = etree.SubElement(current_elem, reg_opening[1].replace(" ","").replace(":",""))
			if reg_opening[2].strip() != "" : current_elem.set("value",reg_opening[2].strip())	# Potential complementary infos

		elif reg_info != None :									# Infos for the current child,
			onemoreline = moretext = reg_info[2]
			while onemoreline.endswith(",") :					# For multiline infos, such as vertex list
				onemoreline = inputfile.readline().strip()
				if onemoreline.endswith("}") :
					current_elem = parents.pop()
				else :
					moretext+=onemoreline
			elem = etree.SubElement(current_elem, reg_info[1])
			elem.text = moretext

		else :													# Unrecognized line. Should'nt happen, it's in case something was not taken into account.
			print("fbx2tree encountered an unknown line :\n"+line)
			stuff = etree.SubElement(current_elem, "stuff")
			stuff.text = line
	inputfile.close()

	if parents != [] :											# Should'nt happen if the FBX and the interpretation is correct.
		print("PARENTS LIST NOT EMPTY")
		print(parents)
		exit(1)

	if verbose : print ("Building tree")
	tree = etree.ElementTree(root)

	if debug :													# Export the tree to xml for debug purposes.
		if verbose : print("writing file")
		with open(filepath+"export\\"+filename+"_fbx.xml", "w", encoding="utf8") as outputfile :
			if verbose : print("prettifying… (Can take a while for big files)")
			stringout = etree.tostring(root).decode()
			pretty = tools.prettifyXml(stringout)
			if verbose : print("writing…")
			outputfile.write(pretty)

	if verbose : print("fbx2tree ended")
	return tree
