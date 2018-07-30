import fbx2tree
import builder_fromfbx

import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="print more stuff", action="store_true")
parser.add_argument("-d", "--debug", help="create intermediate xml files for debug and don't delete other temporary files", action="store_true")
parser.add_argument("--closest", help="Try to stick as close to the original materials in 3dsmax, even if it is at the expense of realism", action="store_true")
parser.add_argument("--realist", help="Try to make materials as realist as possible, even if it is at the expense of fidelity to the original scene", action="store_true")
parser.add_argument("--portable", help="Use relative path to look for textures. Better if you intend to use the scene on an other computer, with textures in a folder", action="store_true")
args = parser.parse_args()
verbose = args.verbose
debug = args.debug
closest = args.closest
realist = args.realist
portable = args.portable
if closest and realist :
	print("Incompatible options : --closest and --realist. Choose one, or neither for a balanced result")
	exit(0)

filename = "scene"

fbxtree = fbx2tree.transform(filename, verbose, debug)
builder_fromfbx.build(filename, fbxtree, verbose, debug, closest, realist, portable)

print("Conversion finished !")
