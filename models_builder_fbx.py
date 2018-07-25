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
					translation = properties["LclTranslation"][-3:] if "LclTranslation" in properties else []
					rotation    = properties["LclRotation"][-3:]    if "LclRotation"    in properties else []

					curr_shape = etree.SubElement(root, "shape")
					curr_shape.set("type", "instance")
					# curr_shape.set("id", links_simple[id])#Get the id of the geometry corresponding

					curr_trans = etree.SubElement(curr_shape, "transform")
					curr_trans.set("name", "toWorld")

					# Add infos to xml only if != 0 to make for a lighter and cleaner file

					if prerotation != [] :
						for i in range(3) :
							if prerotation[i].replace("-","") != "0" :
								curr_prerotat = etree.SubElement(curr_trans, "rotate")
								curr_prerotat.set(dict_index_to_axis[i], "1")
								curr_prerotat.set("angle", prerotation[i])
					

					if translation != [] :
						curr_translat = etree.SubElement(curr_trans, "translate")
						for i in range(3) :
							if translation[i].replace("-","") != "0" :
								curr_translat.set(dict_index_to_axis[i], translation[i])

					if rotation != [] :
						for i in range(3) :
							if rotation[i].replace("-","") != "0" :
								curr_rotat = etree.SubElement(curr_trans, "rotate")
								curr_rotat.set(dict_index_to_axis[i], "1")
								curr_rotat.set("angle", rotation[i])

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
