import time
import re
import xml.etree.cElementTree as etree
import xml.dom.minidom as dom

inputfile = open("simplecube.FBX", "r")

root = etree.Element("root")
parents = []
current_elem = root

line = inputfile.readline().replace("\"","")
while line:
	# Comments in the fbx can give useful informations
	reg_comment = re.match(";(.*)", line.strip())
	#
	reg_opening = re.match("([A-Za-z0-9_]+):(.*) *{", line.strip())
	reg_info = re.match("([A-Za-z0-9_]+): *(.*)", line.strip())
	if len(line.strip())==0 :
		pass
	elif reg_comment!=None :
		comment = etree.SubElement(current_elem, "comment")
		comment.text = reg_comment[1]
	elif reg_opening!=None :
		parents.append(current_elem)
		current_elem = etree.SubElement(current_elem, reg_opening[1].replace(" ","").replace(":",""))
	elif reg_info!=None :
		moretext = ""
		if reg_info[2].endswith(",") :
			moretext+=inputfile.readline().strip()
		while moretext.endswith(",") :
			moretext+=inputfile.readline().strip()
		elem = etree.SubElement(current_elem, reg_info[1])
		elem.text = reg_info[2]+moretext
	elif line.strip().endswith("}") :
		current_elem = parents.pop()
	else :
		print("unknown : "+line)
		stuff = etree.SubElement(current_elem, "stuff")
		stuff.text = line
	line = inputfile.readline().replace("\"","")

if parents != [root] :
	print("PARENTS LIST NOT EMPTY")
	print(parents)

tree = etree.ElementTree(root)
tree.write("simplecubefbx.xml")


xmlstr = dom.parse("simplecubefbx.xml")

# print(xmlstr.toprettyxml())
outputfile = open("simplecubefbx.xml", "w")
outputfile.write(xmlstr.toprettyxml())

time.sleep(1)
