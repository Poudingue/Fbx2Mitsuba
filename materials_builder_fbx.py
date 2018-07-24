import os
import tools
import xml.etree.ElementTree as etree

def build(root, materials, connections, verbose = False, debug = False):
	if verbose : print("materials_builder_fbx launched")

	comment = etree.Comment("Materials with ids")
	root.append(comment)

	for material in materials :
		id, type, obj = material.get("value").replace("::","").split(",")


		shading = material.find("ShadingModel").text
		if shading=="phong" :

			properties = tools.getProperties(material)
			diffuse_color = " ".join(properties["Diffuse"][-3:])
			specular_color = " ".join(properties["Specular"][-3:])
			
			curr_material = etree.SubElement(root, "bsdf")
			curr_material.set("type", "roughdielectric")
			curr_material.set("id", id)

			curr_distrib = etree.SubElement(curr_material, "string")
			curr_distrib.set("name", "distribution")
			# Use phong distribution if phong is specified, for fidelity
			curr_distrib.set("value", "phong")

			curr_albedo = etree.SubElement(curr_material, "spectrum")
			curr_albedo.set("name", "reflectance")
			curr_albedo.set("value", diffuse_color)


			curr_spec_color = etree.SubElement(curr_material, "spectrum")
			curr_spec_color.set("name", "specular reflectance")
			curr_spec_color.set("value", " ".join(str(color) for color in specular_color))
