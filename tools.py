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
		if line == "":
			pass
		elif line.startswith("<") and line.endswith(">") :
			if line.startswith("</"):
				curr_indent-=1
				out+=("" if intext else curr_indent*"\t")+line+"\n"
				intext = False
			elif not line.endswith("/>"):
				out+=curr_indent*"\t"+line.strip()+"\n"
				curr_indent+=1
		else :
			out = out[:-1] + line#Remove the \n from last line and add the text
			intext = True
	return out
