import os
import math
import tools
import xml.etree.ElementTree as etree

def build(root, materials, textures_id, links_param, verbose = False, debug = False, closest = False, realist = False):
	if verbose : print("materials_builder_fbx launched")

	comment = etree.Comment("Materials with ids")
	root.append(comment)

	material_ids = []

	for material in materials :
		id, type, obj = material.get("value").replace("::","").split(",")
		material_ids.append(id)

		# Get linked parameters (mostly textures)
		linked = links_param[id] if id in links_param else []

		shading = material.find("ShadingModel").text

		curr_material = etree.SubElement(root, "bsdf")
		properties = tools.getProperties(material)

		if shading != "phong" and verbose :
			print("Unknown material for object "+id+", using phong")

		diffuse_color = " ".join(properties["Diffuse"][-3:]) if "Diffuse" in properties else (" ".join(properties["DiffuseColor"][-3:]) if "DiffuseColor" in properties else "1 0 0") #Use red if there is no diffuse
		specular_color = " ".join(properties["Specular"][-3:]) if "Specular" in properties else ""
		shininess = properties["ShininessExponent"][-1] if "ShininessExponent" in properties else ""

		# I tried using dielectric, but it only made materials with transmittance, so the plastic was the closer i found.
		curr_material.set("type", "phong" if closest else "roughplastic")
		curr_material.set("id", id)

		curr_distrib = etree.SubElement(curr_material, "string")
		curr_distrib.set("name", "distribution")
		# Use phong for “Balanced” between fidelity and realism.
		# Use ggx otherwise. I chose ggx because of the nice falloff. Note that it can increase convergence time compared to, for example, Beckmann
		curr_distrib.set("value", "ggx" if realist else "phong")

		if "DiffuseColor" in linked :# Use a texture
			curr_albedo = etree.SubElement(curr_material, "ref")
			curr_albedo.set("name", "diffuseReflectance")
			curr_albedo.set("id", linked["DiffuseColor"])
		else :
			curr_albedo = etree.SubElement(curr_material, "spectrum")
			curr_albedo.set("name", "diffuseReflectance")
			curr_albedo.set("value", diffuse_color)


		if specular_color != "" :# Set up only if there is such a color
			curr_spec_color = etree.SubElement(curr_material, "spectrum")
			curr_spec_color.set("name", "specularReflectance")
			curr_spec_color.set("value", " ".join(str(color) for color in specular_color.split(" ")))

		"""
		curr_spec_refl = etree.SubElement(curr_material, "spectrum")
		curr_spec_refl.set("name", "specularTransmittance")
		curr_spec_refl.set("value", "1 0 0")
		"""

		if closest :
			curr_exponent = etree.SubElement(curr_material, "float")
			curr_exponent.set("name", "exponent")
			curr_exponent.set("value", shininess)
		else :
			# Based on this blog post : https://simonstechblog.blogspot.com/2011/12/microfacet-brdf.html
			# But divided by 2, because mitsuba want its roughness in the range 0 - 0.5
			roughness = (1./(float(shininess)+2.)) **(.5) if shininess != "" else 0 # Very glossy material if no shininess found
			curr_roughness = etree.SubElement(curr_material, "float")
			curr_roughness.set("name", "alpha")
			curr_roughness.set("value", str(roughness))
	return material_ids
