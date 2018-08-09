import os
import tools
import config
import xml.etree.ElementTree as etree

dict_index_to_axis = dict([(0, "x"), (1, "y"), (2, "z")])

def build(root, models, links_simple, links_revert, shapes_ids):
	if config.verbose : print("models_builder_fbx launched")

	comment = etree.Comment("Models. Can reference other models, or shapes, or even cameras and lights, and place them in space.")
	root.append(comment)

	for model in models :
		id, type, obj = model.get("value").replace("::","").split(",")
		if id in links_simple :
			for link in links_simple[id] :
				if link in shapes_ids and "0" in links_revert[id] : #For now only models depending on root node to avoid misplacement
					properties = tools.getProperties(model)

					# geomtranslat and geomrotat are to be applied before scaling
					geomtranslat= [tools.str2float2str(numb) for numb in (properties["GeometricTranslation"][-3:] if "GeometricTranslation" in properties else [])]
					geomrotat   = [tools.str2float2str(numb) for numb in (properties   ["GeometricRotation"][-3:] if "GeometricRotation"    in properties else [])]
					scaling     = [tools.str2float2str(numb) for numb in (properties         ["Lcl Scaling"][-3:] if          "Lcl Scaling" in properties else [])]
					rotation    = [tools.str2float2str(numb) for numb in (properties        ["Lcl Rotation"][-3:] if      "Lcl Rotation"    in properties else [])]
					prerotation = [tools.str2float2str(numb) for numb in (properties         ["PreRotation"][-3:] if          "PreRotation" in properties else [])]
					translation = [tools.str2float2str(numb) for numb in (properties     ["Lcl Translation"][-3:] if      "Lcl Translation" in properties else [])]

					curr_shape = etree.SubElement(root, "shape")
					curr_shape.set("type", "instance") # To remove if the code below is used

					# Would work if mitsuba allowed nested instancing.
					# Keep the code and use it if one day it is supported.
					"""
					if "0" in links_revert[id] :
						curr_shape.set("type", "instance")
					else :
						curr_shape.set("type", "shapegroup")
					curr_shape.set("id", id)
					"""

					curr_trans = etree.SubElement(curr_shape, "transform")
					curr_trans.set("name", "toWorld")

					# Add infos to xml only if != 0 to make for a lighter and cleaner file
					# For some reason, the prerotation must come after everything EXCEPT translation.

					if geomtranslat != [] :
						curr_translat2 = etree.SubElement(curr_trans, "translate")
						for i in range(3) :
							curr_string = geomtranslat[i]
							if float(curr_string) != 0 :
								curr_translat2.set(dict_index_to_axis[i], geomtranslat[i])

					if geomrotat != [] :
						for i in range(3) :
							curr_string = geomrotat[i]
							if float(curr_string) != 0 :
								curr_rotat = etree.SubElement(curr_trans, "rotate")
								curr_rotat.set(dict_index_to_axis[i], "1")
								curr_rotat.set("angle", curr_string)

					if scaling != [] :
						curr_scale = etree.SubElement(curr_trans, "scale")
						for i in range(3) :
							curr_string = scaling[i]
							if float(curr_string) != 0 :
								curr_scale.set(dict_index_to_axis[i], scaling[i])

					if rotation != [] :
						for i in range(3) :
							curr_string = rotation[i]
							if float(curr_string) != 0 :
								curr_rotat = etree.SubElement(curr_trans, "rotate")
								curr_rotat.set(dict_index_to_axis[i], "1")
								curr_rotat.set("angle", rotation[i])

					if prerotation != [] :
						for i in range(3) :
							if prerotation[i].replace("-","") != "0" :
								curr_prerotat = etree.SubElement(curr_trans, "rotate")
								curr_prerotat.set(dict_index_to_axis[i], "1")
								curr_prerotat.set("angle", prerotation[i])

					if translation != [] :
						curr_translat = etree.SubElement(curr_trans, "translate")
						for i in range(3) :
							curr_string = translation[i]
							if float(curr_string) != 0 :
								curr_translat.set(dict_index_to_axis[i], translation[i])


					curr_ref = etree.SubElement(curr_shape, "ref")
					curr_ref.set("id", link)
		elif config.verbose :
			print("id "+id+" not in links_simple")
