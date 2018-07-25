# Extract properties from an object in the fbx.
def getProperties(object) :
	dict = {}
	allProp = object.find("Properties70").findall("P")
	for prop in allProp :
		allinfo = prop.text.replace(" ","").split(",")
		for info in allinfo :
			dict[allinfo[0]] = allinfo[1:]
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
def prettifyXml(uglyxml) :
	# This is a faster solution if it takes too long, but there's no indentation :
	# return uglyxml.replace(">", ">\n")

	# We count on the xml being correct
	multiline = uglyxml.replace(">", ">\n").replace("<","\n<").split("\n")

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
