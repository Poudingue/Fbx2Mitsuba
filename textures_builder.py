import os
import tools
import config
from shutil import copyfile
from pathlib import Path
import xml.etree.ElementTree as etree

def build(root, textures, links_param_revert):
	"""
	Creates textures with in the scene.
	Return a list of texture ids.
	"""
	verbose = config.verbose

	if verbose : print("textures_builder_fbx launched")
	comment = etree.Comment("Textures with ids")
	root.append(comment)

	textures_id = {}

	if textures != [] and not os.path.exists(config.filepath+"export\\textures") :
		os.makedirs(config.filepath+"export\\textures")
	copyfile(config.curr_place+"\\missing_texture.png", config.filepath+"export\\textures\\missing_texture.png")

	# Go through all textures in the scene
	for texture in textures :
		id, type, obj      = texture.get("value").replace("::","").split(",")
		rel_reference      = texture.find("RelativeFilename").text.strip()
		abs_reference      = texture.find("FileName").text.strip()

		properties         = tools.getProperties(texture)
		uoff, voff         = properties["Translation"][-3:-1] if "Translation" in properties else ["0", "0"]
		uscaling, vscaling = properties["Scaling"]    [-3:-1] if "Scaling"     in properties else ["1", "1"]

		if rel_reference == "" and abs_reference == "" :
			if verbose : print("Empty reference for id "+id+", replacing with error texture")
			reference = "textures\\missing_texture.png"

		# Try relative path then absolute if it did'nt work
		elif not Path(config.filepath+rel_reference).is_file() :
			if not Path(abs_reference).is_file() :
				if verbose : print("Missing texture : "+rel_reference)
				reference = "textures\\missing_texture.png"
			else :
				new_reference = "textures\\"+id+"."+abs_reference.split(".")[-1]
				copyfile(abs_reference, config.filepath+"export\\"+new_reference)
				reference = new_reference
		else :
			new_reference = "textures\\"+id+"."+abs_reference.split(".")[-1]
			copyfile(config.filepath+rel_reference, config.filepath+"export\\"+new_reference)
			reference = new_reference


		if id not in links_param_revert :
			if verbose : print("Texture "+reference+" never used. Not writing it to file.")
		elif any(reference.lower().endswith(s) for s in [".bmp",".jpg",".png",".tga",".exr"]):

			textures_id[id] = reference
			curr_texture = tools.create_obj(root, "texture", "bitmap", id)
			tools.set_value(curr_texture, "string", "filename", reference)

			# Avoid cluttering for the final file, removing 0 offsets and 1 scaling
			if uoff     != "0" : tools.set_value(curr_texture, "float", "uoffset", uoff)
			if voff     != "0" : tools.set_value(curr_texture, "float", "voffset", voff)
			if uscaling != "1" : tools.set_value(curr_texture, "float", "uscale",  uscaling)
			if vscaling !="-1" : tools.set_value(curr_texture, "float", "vscale",  str(-float(vscaling)))
			# Textures in 3dsmax have their v values inverted compared to mitsuba.

		else :
			print("Unknown texture file type : "+reference.split(".")[-1])
			print("for file : "+reference)
	return textures_id
