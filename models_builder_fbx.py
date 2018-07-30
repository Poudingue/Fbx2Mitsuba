import os
import tools
import xml.etree.ElementTree as etree

dict_index_to_axis = dict([(0, "x"), (1, "y"), (2, "z")])

def build(root, models, links_simple, shapes_ids, verbose = False, debug = False):
	if verbose : print("models_builder_fbx launched")

	comment = etree.Comment("Models. Referencing groupshapes.")
	root.append(comment)

	for model in models :
		id, type, obj = model.get("value").replace("::","").split(",")

		if id in links_simple :
			for link in links_simple[id] :
				if link in shapes_ids :
					properties = tools.getProperties(model)

					prerotation = properties["PreRotation"][-3:] if "PreRotation" in properties else []
					translation = properties["Lcl Translation"][-3:] if "Lcl Translation" in properties else []
					translation2= properties["GeometricTranslation"][-3:] if "GeometricTranslation" in properties else []
					rotation    = properties["Lcl Rotation"][-3:]    if "Lcl Rotation"    in properties else []
					rotation2   = properties["GeometricRotation"][-3:]    if "GeometricRotation"    in properties else []
					scaling     = properties["Lcl Scaling"][-3:]  if "Lcl Scaling" in properties else []

					curr_shape = etree.SubElement(root, "shape")
					curr_shape.set("type", "instance")
					# curr_shape.set("id", links_simple[id])#Get the id of the geometry corresponding

					curr_trans = etree.SubElement(curr_shape, "transform")
					curr_trans.set("name", "toWorld")

					# Add infos to xml only if != 0 to make for a lighter and cleaner file


					# TODO handle e -> ten to the power of, in order to have the correct numbers
					# if rotation2 != [] :
					# 	for i in range(3) :
					# 		if rotation2[i].replace("-","") != "0" and not "e" in rotation2[i] :
					# 			curr_rotat = etree.SubElement(curr_trans, "rotate")
					# 			curr_rotat.set(dict_index_to_axis[i], "1")
					# 			curr_rotat.set("angle", rotation2[i])

					# For some reason, the prerotation must come AFTER the rotation for the scene to be correct

					if rotation != [] :
						for i in range(3) :
							if rotation[i].replace("-","") != "0" and not "e" in rotation[i] :
								curr_rotat = etree.SubElement(curr_trans, "rotate")
								curr_rotat.set(dict_index_to_axis[i], "1")
								curr_rotat.set("angle", rotation[i])
					# if scaling != [] :
					# 	curr_scale = etree.SubElement(curr_trans, "scale")
					# 	for i in range(3) :
					# 		if scaling[i].replace("-","") != "0" and not "e" in scaling[i] :
					# 			curr_scale.set(dict_index_to_axis[i], scaling[i])

					if prerotation != [] :
						for i in range(3) :
							if prerotation[i].replace("-","") != "0" and not "e" in prerotation[i] :
								curr_prerotat = etree.SubElement(curr_trans, "rotate")
								curr_prerotat.set(dict_index_to_axis[i], "1")
								curr_prerotat.set("angle", prerotation[i])

					if translation2 != [] :
						curr_translat2 = etree.SubElement(curr_trans, "translate")
						for i in range(3) :
							if translation2[i].replace("-","") != "0" and not "e" in translation2[i]:
								curr_translat2.set(dict_index_to_axis[i], translation2[i])
					if translation != [] :
						curr_translat = etree.SubElement(curr_trans, "translate")
						for i in range(3) :
							if translation[i].replace("-","") != "0" and not "e" in translation[i]:
								curr_translat.set(dict_index_to_axis[i], translation[i])


					curr_ref = etree.SubElement(curr_shape, "ref")
					curr_ref.set("id", link)
		elif verbose :
			print("id "+id+" not in links_simple")

"""
<shape type="instance" id="/SketchUp/ID461/ID1020/ID1021/ID1021/ID595/ID604">
	<transform name="toWorld">
		<matrix value="0 -1 0 1303.8 1 0 0 -341.3 0 0 1 265.375 0 0 0 1"/>
	</transform>

	<ref id="ID604"/>
</shape>
"""
