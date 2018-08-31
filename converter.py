import sys
import os


if sys.version_info[0] != 3 :
	print("Running in python "+sys.version_info[0]+", should be python 3.")
	print("Please install python 3.7 from the official site python.org")
	print("Exiting now.")
	exit()

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

args = parser.parse_args()

if args.closest and args.realist :
	print("Incompatible options : --closest and --realist. Choose one, or neither for a balanced result")
	exit(0)

fullname = args.file

if fullname.split(".")[-1].lower() != "fbx" :
	print("The file is not an fbx file")
	exit(0)

config.curr_place = os.path.dirname(os.path.abspath(__file__))
config.filename = ".".join(fullname.split(".")[:-1]).split("\\")[-1]#Remove extension, remove path.
config.filepath = "\\".join(fullname.split("\\")[:-1])+"\\"#Keep only path
config.verbose  = args.verbose
config.debug    = args.debug
config.closest  = args.closest
config.realist  = args.realist

fbxtree = fbx2tree.transform()
builder_fromfbx.build(fbxtree)

print("Conversion finished !")
