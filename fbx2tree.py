import re
import xml.etree.cElementTree as etree

def transform(filename, verbose=False, debug=False) :
	if verbose : print("fbx2tree launched")
	root = etree.Element("root")
	parents = []
	current_elem = root
	inputfile = open(filename+".fbx", encoding="utf8")
	# Skip the first line
	# inputfile.readline()

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
		elif len(line.strip())==0 :
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
			elem.text = reg_info[2]+moretext
		else :
			print("unknown : "+line)
			stuff = etree.SubElement(current_elem, "stuff")
			stuff.text = line
	inputfile.close()

	if parents != [] :
		print("PARENTS LIST NOT EMPTY")
		print(parents)
		exit(1)
	tree = etree.ElementTree(root)

	if debug :
		tree.write(filename+"_fbx.xml", encoding="utf8")

	return tree
