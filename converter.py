import ase2tree
import fbx2tree
import fbx_extracter
import ply_builder
import builder_fromfbx
import mitsuba_builder

import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="print more stuff", action="store_true")
parser.add_argument("-d", "--debug", help="create intermediate xml files for debug and don't delete other temporary files", action="store_true")
parser.add_argument("--closest", help="Try to stick as close to the original materials in 3dsmax, even if it is at the expense of realism", action="store_true")
parser.add_argument("--realist", help="Try to make materials as realist as possible, even if it is at the expense of fidelity to the original scene", action="store_true")
args = parser.parse_args()
verbose = args.verbose
debug = args.debug
closest = args.closest
realist = args.realist
if closest and realist :
	print("Incompatible options : --closest and --realist. Choose one, or non for a balanced result")
	exit(0)

filename = "scene"
# asetree = ase2tree.transform(filename, verbose, debug)
fbxtree = fbx2tree.transform(filename, verbose, debug)
# Still experimental
builder_fromfbx.build(filename, fbxtree, verbose, debug, closest, realist)

# fbx_extracter.extract(fbxtree, verbose, debug)
# ply_builder.build(asetree, verbose, debug)
# mitsuba_builder.build(filename, asetree, verbose, debug, twosided=True)

if not debug :
	shutil.rmtree("fbxinfos")
	shutil.rmtree("materials")

print("Conversion finished !")
