import os
from io import StringIO
import math
import config
import xml.etree.ElementTree as etree
from PIL import Image

# Open an image, make it black and white, limit the value to .5 and save it if necessaryself.
# Return a boolean indicating if it is necessary to create a new texture.
def limit_rough(reference, invert) :
	input = Image.open(reference).convert("L")# Convert to luminance
	filename = reference.replace("\\","/").split("/")[-1]
	if invert : input = input.point(lambda px : 255-px)# Invert if necessary
	output = input.point(lambda px : .5*px)
	if not os.path.exists("converted_textures") :
		os.makedirs("converted_textures")
	output.save("converted_textures/"+filename)
	return True

# Useful to make more readable functions
def clamp(value, minv, maxv) :
	return max(minv, min(value, maxv))

# Useful to convert values with powers of ten in it
def str2float2str(str_in) :
	splitted = str_in.split("e")
	if len(splitted) == 2 :
		return "%.10f" % (float(splitted[0])*10**int(splitted[1])) # allow 10 digits
	else :
		return splitted[0]

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

# Convert a Kelvin temperature to an RGB value
# I know mitsuba allow the creation of “Blackbody” with specification of kelvin temperature,
# But this is not a normalized rgb value like in 3dsmax

# Based on this blog post : https://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
# Will maybe implement something more accurate later (full spectrum instead of rgb ???)
# More material on blackbodies : https://en.wikipedia.org/wiki/Color_temperature
def kelvin2rgb(kelvin) :
	if kelvin < 1000 or kelvin > 40000 :
		print("Kelvin value should be between 1 000 and 40 000, the value will be clamped to match these limits")
	kelvin = clamp(kelvin, 1000, 40000) #Clamp value
	kelvin *= .01 #Divide by 100 to deal with smaller numbers

	red = 255. if kelvin <= 66 else clamp(329.698727446 * (kelvin - 60) ** -.1332047592 ,0, 255)
	green = clamp(99.4708025861 * math.log(kelvin) - 161.1195681661 if kelvin <= 66
		else 288.1221695283 * (kelvin - 60) ** -0.0755148492
		, 0, 255)
	blue =  0 if kelvin <= 19 else clamp(138.5177312231 * math.log(kelvin - 10) - 305.0447927307, 0, 255)
	return red/255, green/255, blue/255 # Convert to a 0-1 range

#
def extract_links(links) :
	dict_simple, dict_invert, dict_params, dict_parinv = {}, {}, {}, {}
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
			# Same for reverse dictionnary
			if splitted[1] not in dict_parinv :
				dict_parinv[splitted[1]] = {}
			dict_parinv[splitted[1]][splitted[3].strip()] = splitted[1]

		elif debug :
			print("Unknown link type : "+splitted[0])

	return(dict_simple, dict_invert, dict_params, dict_parinv)


# Create a xml with correct indentation
# uglyxml must be a string
# /!\ can be changed to a tree as an argument for more efficient processing
def prettifyXml(uglyxml) :
	# This is a faster solution if it takes too long, but it's ugly with no indentation,
	# so use only for debug purposes or if the xml creation takes too long :
	# return uglyxml.replace(">", ">\n")

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
