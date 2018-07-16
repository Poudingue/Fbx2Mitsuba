import ase2tree
import fbx2tree
import fbx_extracter
import ply_builder
import mitsuba_builder

import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="print more stuff", action="store_true")
parser.add_argument("--debug", help="create intermediate xml files for debug and don't delete other temporary files", action="store_true")
args = parser.parse_args()
verbose = args.verbose
debug = args.debug

filename = "scene"
asetree = ase2tree.transform(filename, verbose, debug)
fbxtree = fbx2tree.transform(filename, verbose, debug)
fbx_extracter.extract(fbxtree, verbose, debug)
ply_builder.build(asetree, verbose, debug)
mitsuba_builder.build(filename, asetree, verbose, debug, twosided=True)

if not debug :
	shutil.rmtree("fbxinfos")
	shutil.rmtree("materials")

print("Conversion finished !")
