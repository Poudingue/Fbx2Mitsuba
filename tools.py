from io import StringIO
import xml.etree.ElementTree as etree

# Extract properties from an object in the fbx.
def getProperties(object) :
	dict = {}
	Prop70 = object.find("Properties70")
	if Prop70 != None :
		allProp = Prop70.findall("P")
		for prop in allProp :
			allinfo = prop.text.split(",")
			for info in allinfo :
				dict[allinfo[0]] = [info.strip() for info in allinfo[1:]]
				# if verbose : print(allinfo[0]+" = "+"".join(allinfo[1:]))
	return dict

#
def extract_links(links) :
	dict_simple = {}
	dict_invert = {}
	dict_params = {}
	for link in links :
		splitted = link.text.split(",")
		if splitted[0] == "OO" : # Simple link between 2 objects
			# Dictionnary[id] = multiple links possible
			if splitted[2] not in dict_simple :
				dict_simple[splitted[2]] = []
			dict_simple[splitted[2]].append(splitted[1])
			# Same for reverse dictionnary
			if splitted[1] not in dict_invert :
				dict_invert[splitted[1]] = []
			dict_invert[splitted[1]].append(splitted[2])

		elif splitted[0]=="OP" : # Link concerning a parameter.
			# Dictionnary[id][parameter] =
			if splitted[2] not in dict_params :
				dict_params[splitted[2]] = {}
			dict_params[splitted[2]][splitted[3].strip()] = splitted[1]

		elif debug :
			print("Unknown link type : "+splitted[0])

	return(dict_simple, dict_invert, dict_params)


# Create a xml with correct indentation
# uglyxml must be a string
# /!\ can be changed to a tree as an argument for more efficient processing
def prettifyXml(uglyxml) :
	# This is a faster solution if it takes too long, but it's ugly with no indentation
	return uglyxml.replace(">", ">\n")

	"""
	# Code found here : https://gist.github.com/mahmoud/3081869
	# Doesn't seem to work properly
	indent="   "
	if not hasattr(uglyxml, "read"): # ElementTree uses file-like objects
		fn = StringIO(uglyxml)  # cStringIO doesn't support UTF-8
	else :
		fn = uglyxml
	cursor = 0
	out_list = []
	for event, elem in etree.iterparse(fn, events=('start', 'end')):
		if event == 'start':
			attrs = ' '.join([k+'="'+v+'"' for k, v in elem.items()])
			cur_tag = ('<{tag} {attrs}>'.format(tag=elem.tag, attrs=attrs) if attrs else '<{tag}>'.format(tag=elem.tag))
			if elem.text is None:
				had_txt = False
				txt = '\n'
			else:
				had_txt = True
				txt = elem.text
				out_list.extend([indent*cursor, cur_tag, txt])
				cursor += 1
		else :
			cursor -= 1
			cur_ind = cursor*indent if not had_txt else ''
			out_list.extend([cur_ind, '</{0}>'.format(elem.tag), '\n'])
			had_txt = False
	return ''.join(out_list)

	"""
	multiline = uglyxml.replace(">", ">\n").replace("<","\n<").split("\n")
	print("splitted")
	out = ""
	curr_indent = 0
	intext = False # To avoid indenting after a text
	for line in multiline :
		if line == "" :
			pass
		elif line.startswith("<") and line.endswith(">") :
			if line.startswith("</") :
				curr_indent-=1
				out+=("" if intext else curr_indent*"\t")+line+"\n"
				intext = False
			elif line.endswith("/>") or line.startswith("<!") :
				# one-line tag or comment. don't add indentation
				out+=curr_indent*"\t"+line+"\n"
			else :
				out+=curr_indent*"\t"+line+"\n"
				curr_indent+=1
		else :
			out = out[:-1] + line#Remove the \n from last line and add the text
			intext = True

	return out
