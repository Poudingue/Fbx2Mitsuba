import os
import tools
import config
import xml.etree.ElementTree as etree

def build(root, textures, links_param_revert):
	verbose = config.verbose

	if verbose : print("textures_builder_fbx launched")
	comment = etree.Comment("Textures with ids")
	root.append(comment)

	textures_id = {}

	# Go through all textures in the scene
	for texture in textures :
		id, type, obj      = texture.get("value").replace("::","").split(",")
		reference          = texture.find("RelativeFilename" if config.portable else "FileName").text
		uoff, voff         = texture.find("ModelUVTranslation").text.split(",")
		uscaling, vscaling = texture.find("ModelUVScaling"    ).text.split(",")

		if reference == "" :
			if verbose : print("Empty reference for id "+id+", replacing with error texture")
			reference = "missing_texture.png"

		if id not in links_param_revert :
			if verbose : print("Texture "+reference+" never used. Not writing it to file.")
		elif reference.lower().endswith("dds") :
			if verbose : print("dds format not supported")#(yet ?)
		elif any(reference.lower().endswith(s) for s in [".bmp",".jpg",".png",".tga",".exr"]):

			textures_id[id] = reference

			curr_texture = etree.SubElement(root, "texture")
			curr_texture.set("type", "bitmap")
			curr_texture.set("id", id)

			reference_texture = etree.SubElement(curr_texture, "string")
			reference_texture.set("name", "filename")
			reference_texture.set("value", reference)

			# Avoid cluttering for the final file, removing 0 offsets and 1 scaling
			# Does'nt seem to change when texture is scaled/tiled
			if uoff != "0" :
				uoffset = etree.SubElement(curr_texture, "float")
				uoffset.set("name", "uoffset")
				uoffset.set("value", uoff)

			if voff != "0" :
				voffset = etree.SubElement(curr_texture, "float")
				voffset.set("name", "voffset")
				voffset.set("value", voff)

			if uscaling != "1" :
				uscale = etree.SubElement(curr_texture, "float")
				uscale.set("name", "uscale")
				uscale.set("value", uscaling)

			# For some reason textures in 3dsmax have their v values inverted compared to mitsuba.
			if vscaling != "-1" :
				vscale = etree.SubElement(curr_texture, "float")
				vscale.set("name", "vscale")
				vscale.set("value", str(-float(vscaling)))

		else :
			print("Unknown texture file type : "+reference.split(".")[-1])
			print("for file : "+reference)
	return textures_id
