import os
import math
import tools
import config
import xml.etree.ElementTree as etree

def set_texture(target, linked, nameoftexture, scale = "1") :# If unspecified, the scale is 1
	"""
	Try to set a texture for the target. Returns True in case of success, or False in case of failure.
	"""
	if nameoftexture in linked :
		if scale != "1" :
			target = tools.create_obj(target, "texture", "scale")
			tools.set_value(target, "float", "scale", scale)
		else :
			target = tools.new_obj("texture", "bitmap")
		tools.set_ref(target, linked[nameoftexture])
		return target
	return False


def build(root, materials, textures_id, links_param, links_param_revert):
	"""
	Creates materials with ids in the scene.
	Returns a list of materials id.
	"""
	if config.verbose : print("materials_builder_fbx launched")
	comment = etree.Comment("Materials with ids")
	root.append(comment)

	material_ids = []

	for material in materials :
		id, type, obj = material.get("value").replace("::","").split(",")
		material_ids.append(id)

		# Get linked parameters (only textures ?)
		linked = links_param[id] if id in links_param else []
		properties = tools.getProperties(material)

		diffuse_color  =(" ".join(properties["Diffuse"][-3:])         if "Diffuse"           in properties
		else(" ".join(properties["DiffuseColor"][-3:])    if "DiffuseColor"      in properties else "1 0 0")) #Use red if there is no diffuse, for debug
		specular_color = " ".join(properties["Specular"][-3:])        if "Specular"          in properties else "1 1 1"
		shininess      =          properties["ShininessExponent"][-1] if "ShininessExponent" in properties else ""

		# If bumpmap is on, use it
		if ("3dsMax|Parameters|bump_map" in linked) :# Use bump map
			scale = properties["3dsMax|Parameters|bump_map_amt"][-1]
			curr_bumpmod = tools.create_obj(root, "bsdf", "bumpmap", id)
			set_texture(curr_bumpmod, linked, "3dsMax|Parameters|bump_map", scale)
			curr_material = etree.SubElement(curr_bumpmod, "bsdf")
		else :
			curr_material = etree.SubElement(root, "bsdf")
			curr_material.set("id", id)

		# Roughness
		if "3dsMax|Parameters|roughness" in properties :
			if "3dsMax|Parameters|roughness_map" in linked : # Use a texture
				inverted_roughness = properties["3dsMax|Parameters|roughness_inv"][-1] == "1"
				texture_properties = textures_id[linked["3dsMax|Parameters|roughness_map"]]
				filename = texture_properties["reference"].replace("\\","/").split("/")[-1]

				roughness_reference = tools.roughness_convert(filename, inverted_roughness)

				uoff, voff         = texture_properties["Translation"][-3:-1] if "Translation" in texture_properties else ["0", "0"]
				uscaling, vscaling = texture_properties["Scaling"]    [-3:-1] if "Scaling"     in texture_properties else ["1", "1"]

				# Create a new texture
				curr_roughness = tools.new_obj("texture", "bitmap")
				curr_roughness.set("name", "alpha")

				# Avoid cluttering for the final file, removing 0 offsets and 1 scaling
				if uoff     != "0" : tools.set_value(curr_roughness, "float", "uoffset", uoff)
				if voff     != "0" : tools.set_value(curr_roughness, "float", "voffset", voff)
				if uscaling != "1" : tools.set_value(curr_roughness, "float", "uscale",  uscaling)
				if vscaling !="-1" : tools.set_value(curr_roughness, "float", "vscale",  str(-float(vscaling)))

				tools.set_value(curr_roughness, "string", "filename", roughness_reference)
			else : # Use a value
				roughness = .5*float(properties["3dsMax|Parameters|roughness"][-1])
				if roughness == 0 :
					curr_roughness = None
				else :
					curr_roughness = etree.Element("float")
					curr_roughness.set("name", "alpha")
					curr_roughness.set("value", str(roughness))
		else :
			curr_roughness = None
			# Based on this blog post : https://simonstechblog.blogspot.com/2011/12/microfacet-brdf.html
			# √(2/(α+2))
			# But divided by 2, because of mitsuba's roughness scale
			roughness = .5 * (2./(float(shininess)+2.)) ** (.5)
			curr_roughness = etree.Element("float")
			curr_roughness.set("name", "alpha")
			curr_roughness.set("value", str(roughness))

		# Specular transmittance
		if "3dsMax|Parameters|transparency" in properties and float(properties["3dsMax|Parameters|transparency"][-1]) > 0 :
			transp = 1 - float(properties["3dsMax|Parameters|transparency"][-1])
			transp_color = " ".join(properties["3dsMax|Parameters|trans_color"][-4:-1])
			curr_material.set("type", "blendbsdf")

			tools.set_value(curr_material, "float", "weight", str(transp))
			# Transparent material for the blend
			curr_transp = tools.create_obj(curr_material, "bsdf", "roughdielectric")
			tools.set_value(curr_transp, "string",   "distribution",          config.distrib)
			tools.set_value(curr_transp, "spectrum", "specularTransmittance", transp_color)
			tools.set_value(curr_transp, "float",    "alpha",                 properties["3dsMax|Parameters|trans_roughness"][-1])

			if "3dsMax|Parameters|trans_ior" in properties :
				tools.set_value(curr_transp, "float", "intIOR", properties["3dsMax|Parameters|trans_ior"][-1])

			# Non-transparent part of the material
			curr_material = etree.SubElement(curr_material, "bsdf")

		# Metalness
		metalness = float(properties["3dsMax|Parameters|metalness"][-1]) if "3dsMax|Parameters|metalness" in properties else 0
		if metalness > 0 :
			if metalness < 1 :
				curr_material.set("type", "blendbsdf")
				tools.set_value(curr_material, "float", "weight",
					str(1 - float(properties["3dsMax|Parameters|metalness"][-1])))# 1 - Metalness
				curr_metal = tools.create_obj(curr_material, "bsdf", "roughconductor" if curr_roughness != None else "conductor")
			else :
				curr_material.set("type", "roughconductor" if curr_roughness != None else "conductor")
				curr_metal = curr_material
			# Metal part of the material
			tools.set_value(curr_metal, "string"  , "distribution", config.distrib)
			if curr_roughness != None :
				curr_metal.append(curr_roughness)
			tools.set_value(curr_metal, "string"  , "material"    , "none") # Perfect mirror, the color is set via specularReflectance.
			# Copy-paste from diffuse, this is what 3dsmax uses
			if "DiffuseColor" in linked :# Use a texture
				tools.set_value(curr_metal, "ref", "specularReflectance", linked["DiffuseColor"])
			elif "3dsMax|Parameters|base_color_map" in linked :
				tools.set_value(curr_metal, "ref", "specularReflectance", linked["3dsMax|Parameters|base_color_map"])
			elif diffuse_color != "1 1 1":
				tools.set_value(curr_metal, "spectrum", "specularReflectance", diffuse_color)
			# else it's the default of 1 1 1

			# Non-metal part of the material
			if metalness < 1 : curr_material = etree.SubElement(curr_material, "bsdf")

		# Non transmitting and non-metal part of the material. Only if metalness < 1
		if metalness < 1 :
			curr_material.set("type", "phong" if config.closest else ("roughplastic" if curr_roughness != None else "plastic"))
			tools.set_value(curr_material, "string", "distribution", config.distrib)

			# keep the original diffuse independantly of ior.
			if config.realist :
				tools.set_value(curr_material, "boolean", "nonlinear", "true")

			if "DiffuseColor" in linked :# Use a texture
				tools.set_value(curr_material, "ref", "diffuseReflectance", linked["DiffuseColor"])
			elif "3dsMax|Parameters|base_color_map" in linked :
				tools.set_value(curr_material, "ref", "diffuseReflectance", linked["3dsMax|Parameters|base_color_map"])
			else :
				tools.set_value(curr_material, "spectrum", "diffuseReflectance", diffuse_color)

			if specular_color != "1 1 1" : # Set up only if there is such a color
				curr_spec_color = etree.SubElement(curr_material, "spectrum")
				curr_spec_color.set("name", "specularReflectance")
				curr_spec_color.set("value", specular_color)

			if "3dsMax|Parameters|coat_ior" in properties :
				ior = properties["3dsMax|Parameters|coat_ior"][-1]
				tools.set_value(curr_material, "float", "intIOR", ior)

			if config.closest and shininess != "" :
				tools.set_value(curr_material, "float", "exponent", shininess)
			elif curr_roughness != None :
				curr_material.append(curr_roughness)

	return material_ids
