import os
import tools
import config
from pathlib import Path
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
		properties = tools.getProperties(texture)
		uoff, voff         = properties["Translation"][-3:-1] if "Translation" in properties else ["0", "0"]
		uscaling, vscaling = properties["Scaling"]    [-3:-1] if "Scaling"     in properties else ["1","-1"]
		# uoff, voff         = texture.find("ModelUVTranslation").text.split(",")
		# uscaling, vscaling = texture.find("ModelUVScaling"    ).text.split(",")

		if reference == "" :
			if verbose : print("Empty reference for id "+id+", replacing with error texture")
			reference = "missing_texture.png"

		if id not in links_param_revert :
			if verbose : print("Texture "+reference+" never used. Not writing it to file.")
		elif reference.lower().endswith("dds") :
			if verbose : print("dds format not supported")#(yet ?)
		elif any(reference.lower().endswith(s) for s in [".bmp",".jpg",".png",".tga",".exr"]):

			textures_id[id] = reference
			if not Path(reference).is_file() :
				if verbose : print("Missing texture : "+reference)
				reference = "missing_texture.png"
			curr_texture = tools.create_obj(root, "texture", "bitmap", id)
			tools.set_value(curr_texture, "string", "filename", reference)

			# Avoid cluttering for the final file, removing 0 offsets and 1 scaling
			if uoff != "0"      : tools.set_value(curr_texture, "float", "uoffset", uoff)
			if voff != "0"      : tools.set_value(curr_texture, "float", "voffset", voff)
			if uscaling != "1"  : tools.set_value(curr_texture, "float", "uscale",  uscaling)
			if vscaling != "-1" : tools.set_value(curr_texture, "float", "vscale",  str(-float(vscaling)))
			# For some reason textures in 3dsmax have their v values inverted compared to mitsuba.

		else :
			print("Unknown texture file type : "+reference.split(".")[-1])
			print("for file : "+reference)
	return textures_id
