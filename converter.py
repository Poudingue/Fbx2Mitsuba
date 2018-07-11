import os
import shutil
import ase2xml
import fbx_info_extract
import plybuilder
import asexml2mitsubaxml

filename = "scene"
ase2xml.ase2xmlconvert(filename)
fbx_info_extract.fbx_extract(filename)
plybuilder.convert(filename)
asexml2mitsubaxml.convert(filename)

"""
os.remove(filename+"_ase.xml")
os.remove(filename+"_fbx.xml")
shutil.rmtree("fbxinfos")
shutil.rmtree("materials")
"""
