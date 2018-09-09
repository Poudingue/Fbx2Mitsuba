import os
from io import StringIO
import math
import config
import random
import xml.etree.ElementTree as etree

try :
	from PIL import Image
	pilimported = True
except ImportError:
	pilimported = False

missing = object()


def set_value(parent, type, name, value) :
	"""
	Sets a value in the format Mitsuba Renderer expects
	"""
	curr_elem = etree.SubElement(parent, type)
	curr_elem.set("name", name)
	curr_elem.set("id" if type in ["ref", "shapegroup"] else "value", value) # The can be an id
	return curr_elem # In case we need it somewhere


def set_ref(parent, id) :
	"""
	Sets a reference in the format Mitsuba Renderer expects
	"""
	curr_ref = etree.SubElement(parent, "ref")
	curr_ref.set("id", id)
	return curr_ref


def create_obj(parent, object, type, id=missing) :
	"""
	Create an object in the format Mitsuba Renderer expects. Id is optionnal, used for referencing.
	"""
	curr_elem = etree.SubElement(parent, object)
	curr_elem.set("name" if object == "transform" else "type", type)
	if id is not missing :
		curr_elem.set("id", id)
	return curr_elem


def new_obj(object, type, id=missing) :
	"""
	Create an object with no parent in the format Mitsuba Renderer expects. Id is optionnal, used for referencing.
	"""
	curr_elem = etree.Element(object)
	curr_elem.set("type", type)
	if id is not missing :
		curr_elem.set("id", id)
	return curr_elem


def roughness_convert(reference, invert) :
	"""
	Open an image and modify it to acomodate for the way Mitsuba Renderer interprets roughness.
	returns the reference for the image.
	"""
	# Conversion for Mitsuba : no value above .5, and if this is a glossinness map, do an inversion.
	# I'm doing a linear inversion, it's closest to the way it seems to behave in 3ds Max.
	# However, it's not perfect, there's maybe a need for a custom conversion.
	if not pilimported :
		print("Pillow doesn't seem to be installed, roughness maps may cause some problems.")
		return reference
	reference = config.filepath+"export\\textures\\"+reference
	input = Image.open(reference)# Convert to luminance
	# ri means roughnes inverted, r just roughness.
	# Different names in case the same texture is used for roughness, revert roughness, and something else.
	filename = ".".join(reference.split("\\")[-1].split(".")[:-1])+("_ri."if invert else "_r.")+reference.split(".")[-1]

	# Dither it ? There is a loss of precision with halving and reconverting to 8bit channels
	# With simple random function, it does'nt work, the lambda seem to work by blocks in the image.
	# Random with pixel coordinates as seed should work
	if invert : # Linear inversion : -> convert to linear, invert , reconvert to perceptual
		# This is intended if i use 254 instead of 255, this is to ensure that the smoothest surfaces give a pitch black roughness, instead of the greyish tone obtained otherwise.
		output = input.point(lambda px : int(.5 * 255. * (max(0, 1 - (float(px)/254.)**(2.2)))**(1./2.2)))
	else :
		output = input.point(lambda px : int(.5 * 255. * (float(px)/255.)))

	savedir = config.filepath+"export\\textures"
	if not os.path.exists(savedir) :
		os.makedirs(savedir)
	output.save(savedir+"\\"+filename)
	return "textures\\"+filename


def clamp(value, minv, maxv) :
	"""
	Clamp a value
	"""
	return max(minv, min(value, maxv))


def str2float2str(str_in) :
	"""
	Convert powers of ten to decimal strings.
	"""
	splitted = str_in.split("e")
	if len(splitted) == 2 :
		return "%.10f" % (float(splitted[0])*10**int(splitted[1])) # allow 10 digits
	else :
		return splitted[0]


# Extract properties from an object in the fbx.
def getProperties(object) :
	"""
	Extracts and returns properties of an object from the FBX tree.
	"""
	dict = {}
	Prop70 = object.find("Properties70")
	if Prop70 != None :
		allProp = Prop70.findall("P")
		for prop in allProp :
			allinfo = prop.text.split(",")
			for info in allinfo :
				dict[allinfo[0]] = [info.strip() for info in allinfo[1:]]
	return dict


def kelvin2rgb(kelvin) :
	"""
	Converts kelvin value to rgb values
	"""
	if kelvin < 1000 or kelvin > 20000 :
		print("Kelvin values should be between 1 000 and 20 000, the value will be clamped to match these limits")
	kelvin = clamp(kelvin, 1000, 20000) #Clamp value
	kelvin /= 1000 # Divide by 1000 to deal with smaller numbers

	r_start_transient, r_end_transient = 2, 5
	r_lower, r_higher = -44.1688669323003 * math.log(kelvin) + 87.2872299941858, -5.05773731937356 * math.log(kelvin) + 33.0778432820841
	r_mix = clamp((kelvin - r_start_transient)/(r_end_transient - r_start_transient), 0, 1)
	red = (1-r_mix)*r_lower + r_mix*r_higher

	g_unlimited = 18.9671759008472 * math.log(kelvin) + 2.28121373699985
	g_mix = min(g_unlimited/25.3, 1)
	green = g_mix * 25.3 + (1-g_mix) * g_unlimited

	blue = max(0, 19.178918414813 * math.log(kelvin) - 12.4836627601213)

	average = red + green + blue / 3
	return red/average, green/average, blue/average


def extract_links(links) :
	"""
	Extracts relations between objects.
	Returns dictionnaries and revert dictionnaries for simple links, and for links with parameters.
	"""
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


# Dictionnary for the transform
dict_index_to_axis = dict([(0, "x"), (1, "y"), (2, "z")])

def transform_lookat(current_object, origin, target, up=missing) :
	"""
	Apply a “lookat” transform to an object.
	"""
	current_transform = current_object.find("transform")
	if current_transform == None : current_transform = create_obj(current_object, "transform", "toWorld")
	curr_lookat = etree.SubElement(current_transform, "lookat")
	curr_lookat.set("origin", origin)
	curr_lookat.set("target", target)
	if up is not missing : curr_lookat.set("up", up)

def transform_lookat_from_properties(current_object, properties) :
	"""
	Apply a “lookat” transform to an object from a list of properties.
	"""
	transform_lookat(
		current_object,
		" ".join(properties["Position"][-3:]),
		" ".join(properties["InterestPosition"][-3:]),
		" ".join(properties["UpVector"][-3:]) if "UpVector" in properties else missing
	)


def transform_object(current_object, properties) :
	"""
	Add the correct transformations to an object from properties
	"""
	current_transform = current_object.find("transform")
	if current_transform == None : current_transform = create_obj(current_object, "transform", "toWorld")

	# geomtranslat and geomrotat are to be applied before scaling
	postrotation = [str2float2str(numb) for numb in (properties        ["PostRotation"][-3:] if         "PostRotation" in properties else [])] # Useful ?
	geomtranslat = [str2float2str(numb) for numb in (properties["GeometricTranslation"][-3:] if "GeometricTranslation" in properties else [])]
	geomrotat    = [str2float2str(numb) for numb in (properties   ["GeometricRotation"][-3:] if    "GeometricRotation" in properties else [])]
	scaling      = [str2float2str(numb) for numb in (properties         ["Lcl Scaling"][-3:] if          "Lcl Scaling" in properties else [])]
	rotation     = [str2float2str(numb) for numb in (properties        ["Lcl Rotation"][-3:] if         "Lcl Rotation" in properties else [])]
	prerotation  = [str2float2str(numb) for numb in (properties         ["PreRotation"][-3:] if          "PreRotation" in properties else [])]
	translation  = [str2float2str(numb) for numb in (properties     ["Lcl Translation"][-3:] if      "Lcl Translation" in properties else [])]

	# Add infos to xml only if != 0 to make for a lighter and cleaner final file
	if geomtranslat != [] :
		curr_translat2 = etree.SubElement(current_transform, "translate")
		for i in range(3) :
			curr_string = geomtranslat[i]
			if float(curr_string) != 0 :
				curr_translat2.set(dict_index_to_axis[i], geomtranslat[i])

	if geomrotat != [] :
		for i in range(3) :
			curr_string = geomrotat[i]
			if float(curr_string) != 0 :
				curr_rotat = etree.SubElement(current_transform, "rotate")
				curr_rotat.set(dict_index_to_axis[i], "1")
				curr_rotat.set("angle", curr_string)

	if scaling != [] :
		curr_scale = etree.SubElement(current_transform, "scale")
		for i in range(3) :
			curr_string = scaling[i]
			if float(curr_string) != 0 :
				curr_scale.set(dict_index_to_axis[i], scaling[i])

	if rotation != [] :
		for i in range(3) :
			curr_string = rotation[i]
			if float(curr_string) != 0 :
				curr_rotat = etree.SubElement(current_transform, "rotate")
				curr_rotat.set(dict_index_to_axis[i], "1")
				curr_rotat.set("angle", rotation[i])

	if prerotation != [] :
		for i in range(3) :
			if float(prerotation[i]) != 0 :
				curr_prerotat = etree.SubElement(current_transform, "rotate")
				curr_prerotat.set(dict_index_to_axis[i], "1")
				curr_prerotat.set("angle", prerotation[i])

	if translation != [] :
		curr_translat = etree.SubElement(current_transform, "translate")
		for i in range(3) :
			curr_string = translation[i]
			if float(curr_string) != 0 :
				curr_translat.set(dict_index_to_axis[i], translation[i])


def prettifyXml(uglyxml) :
	"""
	Create and returns a correct XML formating from a string.
	"""
	# /!\ NOT EFFICIENT FOR HUGE TREES
	# This is a faster solution if it takes too long, but it's ugly with no indentation,
	# so use only for debug purposes or if the xml creation takes too long :
	""" return uglyxml.replace(">", ">\n") """

	multiline = uglyxml.replace(">", ">\n").replace("<","\n<").split("\n")
	out = ""
	curr_indent = 0
	intext = False # To avoid indenting after a text
	for line in multiline :
		if line == "" : pass
		elif line.startswith("<") and line.endswith(">") :
			if line.startswith("</") :
				curr_indent-=1
				out += ("" if intext else curr_indent*"\t")+line+"\n"
				intext = False
			elif line.endswith("/>") or line.startswith("<!") :
				# one-line tag or comment. don't add indentation
				out += curr_indent*"\t"+line+"\n"
			else :
				out += curr_indent*"\t"+line+"\n"
				curr_indent+=1
		else :
			out = out[:-1] + line#Remove the \n from last line and add the text
			intext = True

	return out
