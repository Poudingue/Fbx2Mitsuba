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

			curr_bumpmod = etree.SubElement(root, "bsdf")
			curr_bumpmod.set("id", id)
			curr_bumpmod.set("type", "bumpmap")
			curr_bumpmap = etree.SubElement(curr_bumpmod, "texture")
			curr_bumpmap.set("type", "scale")
			curr_scale   = etree.SubElement(curr_bumpmap, "float")
			curr_scale.set("name", "scale")
			curr_scale.set("value", properties["3dsMax|Parameters|bump_map_amt"][-1])
			curr_texture = etree.SubElement(curr_bumpmap, "ref")
			curr_texture.set("id",      linked["3dsMax|Parameters|bump_map"])

			curr_material = etree.SubElement(curr_bumpmod, "bsdf")
		else :
			curr_material = etree.SubElement(root, "bsdf")
			curr_material.set("id", id)

		if shading != "phong" and config.verbose :
			print("Unknown material for object "+id+", using phong")

		diffuse_color  =(" ".join(properties["Diffuse"][-3:])         if "Diffuse"           in properties
			       else (" ".join(properties["DiffuseColor"][-3:])    if "DiffuseColor"      in properties else "1 0 0")) #Use red if there is no diffuse
		specular_color = " ".join(properties["Specular"][-3:])        if "Specular"          in properties else ""
		shininess      =          properties["ShininessExponent"][-1] if "ShininessExponent" in properties else ""

		# I tried using dielectric, but it only made materials with transmittance
		curr_material.set("type", "phong" if config.closest else "roughplastic")

		curr_distrib = etree.SubElement(curr_material, "string")
		curr_distrib.set("name", "distribution")
		# Use phong for “Balanced” between fidelity and realism.
		# Use ggx otherwise. I chose ggx because of the nice falloff. Note that it can increase convergence time compared to, for example, Beckmann
		curr_distrib.set("value", "ggx" if config.realist else "phong")

		# keep the original diffuse independantly of ior.
		if config.realist :
			nonlin = etree.SubElement(curr_material, "boolean")
			nonlin.set("name", "nonlinear")
			nonlin.set("value", "true")

		if "DiffuseColor" in linked :# Use a texture
			curr_albedo = etree.SubElement(curr_material, "ref")
			curr_albedo.set("name", "diffuseReflectance")
			curr_albedo.set("id", linked["DiffuseColor"])
		elif "3dsMax|Parameters|base_color_map" in linked :
			curr_albedo = etree.SubElement(curr_material, "ref")
			curr_albedo.set("name", "diffuseReflectance")
			curr_albedo.set("id", linked["3dsMax|Parameters|base_color_map"])
		else :
			curr_albedo = etree.SubElement(curr_material, "spectrum")
			curr_albedo.set("name", "diffuseReflectance")
			curr_albedo.set("value", diffuse_color)

		# Not physically based, except for metals. Include ?
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
				if tools.roughness_convert(textures_id[linked["3dsMax|Parameters|roughness_map"]], inverted_roughness) :
					# Create a new texture
					curr_roughness = etree.SubElement(curr_material, "texture")
					curr_roughness.set("name", "alpha")
					curr_roughness.set("type", "bitmap")
					vscale = etree.SubElement(curr_roughness, "float")
					vscale.set("name", "vscale")
					vscale.set("value", "-1")
					filename = textures_id[linked["3dsMax|Parameters|roughness_map"]].replace("\\","/").split("/")[-1]
					reference_texture = etree.SubElement(curr_roughness, "string")
					reference_texture.set("name", "filename")
					reference_texture.set("value", "converted_textures/"+filename)
				else :
					curr_roughness = etree.SubElement(curr_material, "ref")
					curr_roughness.set("name", "alpha")
					curr_roughness.set("id", linked["3dsMax|Parameters|roughness_map"])
			else : # Use a value
				roughness = properties["3dsMax|Parameters|roughness"][-1]
				curr_roughness = etree.SubElement(curr_material, "float")
				curr_roughness.set("name", "alpha")
				curr_roughness.set("value", str(roughness))

			if "3dsMax|Parameters|coat_ior" in properties :
				ior = properties["3dsMax|Parameters|coat_ior"][-1]
				curr_ior = etree.SubElement(curr_material, "float")
				curr_ior.set("name", "intIOR")
				curr_ior.set("value", ior)

		else :
			if config.closest : # Use the Phong plugin
				curr_exponent = etree.SubElement(curr_material, "float")
				curr_exponent.set("name", "exponent")
				curr_exponent.set("value", shininess)
			else :
				# Based on this blog post : https://simonstechblog.blogspot.com/2011/12/microfacet-brdf.html
				# √(2/(α+2))
				# But limited to .5, because mitsuba doesn't support higher roughness
				roughness = min((2./((float(shininess)+2.)) ** (.5)), .5) if shininess != "" else 0 # Very glossy material if no shininess found
				curr_roughness = etree.SubElement(curr_material, "float")
				curr_roughness.set("name", "alpha")
				curr_roughness.set("value", str(roughness))
	return material_ids
