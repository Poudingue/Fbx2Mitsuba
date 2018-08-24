import shutil
import argparse
import fbx2tree
import builder_fromfbx
import time
# config is useful to keep info for the different modules
import config

parser = argparse.ArgumentParser()
parser.add_argument("file", help="file")
parser.add_argument("-v", "--verbose", help="Print more stuff", action="store_true")
parser.add_argument("-d", "--debug",   help="Create intermediate xml files for debug", action="store_true")
parser.add_argument("--closest",       help="Try to stick as close to the original materials in 3dsmax, even if it is at the expense of realism", action="store_true")
parser.add_argument("--realist",       help="Try to make materials as realist as possible, even if it is at the expense of fidelity to the original scene", action="store_true")
parser.add_argument("--portable",      help="Use relative path to look for textures. Better if you intend to use the scene on an other computer, with textures in a folder", action="store_true")
# TODO replace this version of portable with a version creating a subfolder with all the necessary assets in it

args = parser.parse_args()

if args.closest and args.realist :
	print("Incompatible options : --closest and --realist. Choose one, or neither for a balanced result")
	exit(0)

fullname = (args.file).split(".")

if fullname[-1].lower() != "fbx" :
	print("The file is not an fbx file")
	exit(0)

config.filename = ".".join(fullname[:-1])
config.verbose  = args.verbose
config.debug    = args.debug
config.closest  = args.closest
config.realist  = args.realist
config.portable = args.portable

fbxtree = fbx2tree.transform()
builder_fromfbx.build(fbxtree)

print("Conversion finished !")
time.sleep(1)
