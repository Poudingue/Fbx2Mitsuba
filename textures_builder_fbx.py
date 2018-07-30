import os
import tools
import xml.etree.ElementTree as etree

def build(root, textures, verbose = False, debug = False, portable = False):
	if verbose : print("textures_builder_fbx launched")
	comment = etree.Comment("Textures with ids")
	root.append(comment)

	textures_id = []

	# Go through all textures in the scene
	for texture in textures :
		id, type, obj = texture.get("value").replace("::","").split(",")
		reference = texture.find("RelativeFilename" if portable else "FileName").text
		uoff, voff = texture.find("ModelUVTranslation").text.split(",")
		uscaling, vscaling = texture.find("ModelUVScaling").text.split(",")

		if any(reference.endswith(s) for s in [".bmp",".jpg",".png",".tga",".exr"]):

			textures_id.append(id)

			curr_texture = etree.SubElement(root, "texture")
			curr_texture.set("type", "bitmap")
			curr_texture.set("id", id)

			reference_texture = etree.SubElement(curr_texture, "string")
			reference_texture.set("name", "filename")
			reference_texture.set("value", reference)

			uoffset = etree.SubElement(curr_texture, "float")
			uoffset.set("name", "uoffset")
			uoffset.set("value", uoff)
			voffset = etree.SubElement(curr_texture, "float")
			voffset.set("name", "uoffset")
			voffset.set("value", voff)

			uscale = etree.SubElement(curr_texture, "float")
			uscale.set("name", "uscale")
			uscale.set("value", uscaling)
			vscale = etree.SubElement(curr_texture, "float")
			vscale.set("name", "vscale")
			vscale.set("value", vscaling)
		else :
			print("Unknown texture file type : "+reference.split(".")[-1])
			print("for file : "+reference)
