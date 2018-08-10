import os
import math
import tools
import config
import xml.etree.ElementTree as etree

def build(root, materials, textures_id, links_param, links_param_revert):
	if config.verbose : print("materials_builder_fbx launched")
	comment = etree.Comment("Materials with ids")
	root.append(comment)

	material_ids = []

	for material in materials :
		id, type, obj = material.get("value").replace("::","").split(",")
		material_ids.append(id)

		# Get linked parameters (only textures ?)
		linked = links_param[id] if id in links_param else []
		shading = material.find("ShadingModel").text
		properties = tools.getProperties(material)

		if ("3dsMax|Parameters|bump_map_on" in properties
			and properties["3dsMax|Parameters|bump_map_on"][-1] == "1"
			and "3dsMax|Parameters|bump_map" in linked) :# Use bump map

			curr_bumpmod = tools.create_obj(root, "bsdf", "bumpmap", id)
			curr_bumpmap = tools.create_obj(curr_bumpmod, "texture", "scale")
			tools.set_value(curr_bumpmap, "float", "scale", properties["3dsMax|Parameters|bump_map_amt"][-1])

			curr_texture = etree.SubElement(curr_bumpmap, "ref")
			curr_texture.set("id", linked["3dsMax|Parameters|bump_map"])

			curr_material = etree.SubElement(curr_bumpmod, "bsdf")
		else :
			curr_material = etree.SubElement(root, "bsdf")
			curr_material.set("id", id)

		diffuse_color  =(" ".join(properties["Diffuse"][-3:])         if "Diffuse"           in properties
					else(" ".join(properties["DiffuseColor"][-3:])    if "DiffuseColor"      in properties else "1 0 0")) #Use red if there is no diffuse
		specular_color = " ".join(properties["Specular"][-3:])        if "Specular"          in properties else ""
		shininess      =          properties["ShininessExponent"][-1] if "ShininessExponent" in properties else ""

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
		if "3dsMax|Parameters|metalness" in properties and float(properties["3dsMax|Parameters|metalness"][-1]) > 0 :
			curr_material.set("type", "blendbsdf")
			tools.set_value(curr_material, "float", "weight",
				str(1 - float(properties["3dsMax|Parameters|metalness"][-1])))# 1 - Metalness

			# Metal part of the material
			curr_metal = tools.create_obj(curr_material, "bsdf", "roughconductor")
			tools.set_value(curr_metal, "string"  , "distribution", config.distrib)
			tools.set_value(curr_metal, "float"   , "alpha"       , "0") #TODO roughness of the material
			tools.set_value(curr_metal, "string"  , "material"    , "none") # Perfect mirror, the color is set via specularReflectance.
			tools.set_value(curr_metal, "spectrum", "specularReflectance", ".9 .1 0")# TODO debug red to see it, apply “diffuse” color or texture

			# Non-metal part of the material
			curr_material = etree.SubElement(curr_material, "bsdf")

		# Non transmitting and non-metal part of the material
		curr_material.set("type", "phong" if config.closest else "roughplastic")
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

		# Not physically based, except for metals. Include ??
		"""
		if specular_color != "" : # Set up only if there is such a color
			curr_spec_color = etree.SubElement(curr_material, "spectrum")
			curr_spec_color.set("name", "specularReflectance")
			curr_spec_color.set("value", " ".join(str(color) for color in specular_color.split(" ")))
		"""

		# microfacet model if this parameter exists
		if "3dsMax|Parameters|roughness" in properties :
			if "3dsMax|Parameters|roughness_map" in linked : # Use a texture
				inverted_roughness = properties["3dsMax|Parameters|roughness_inv"][-1] == "1"
				reference = tools.roughness_convert(textures_id[linked["3dsMax|Parameters|roughness_map"]], inverted_roughness)
				filename = textures_id[linked["3dsMax|Parameters|roughness_map"]].replace("\\","/").split("/")[-1]

				# Create a new texture
				curr_roughness = tools.create_obj(curr_material, "texture", "bitmap")
				curr_roughness.set("name", "alpha")
				tools.set_value(curr_roughness, "float",  "vscale", "-1")# TODO Use the vscale of the texture
				tools.set_value(curr_roughness, "string", "filename", reference)
			else : # Use a value
				roughness = .5*float(properties["3dsMax|Parameters|roughness"][-1])
				tools.set_value(curr_material, "float",  "alpha", str(roughness))

			if "3dsMax|Parameters|coat_ior" in properties :
				ior = properties["3dsMax|Parameters|coat_ior"][-1]
				tools.set_value(curr_material, "float", "intIOR", ior)

		else :
			if config.closest : # Use the Phong plugin
				tools.set_value(curr_material, "float", "exponent", shininess)
			else :
				# Based on this blog post : https://simonstechblog.blogspot.com/2011/12/microfacet-brdf.html
				# √(2/(α+2))
				# But divided by 2, because mitsuba doesn't support higher roughness
				roughness = 1./((float(shininess)+2.)) ** (.5) if shininess != "" else 0 # Very glossy material if no shininess found
				tools.set_value(curr_material, "float", "alpha", str(roughness))
	return material_ids
