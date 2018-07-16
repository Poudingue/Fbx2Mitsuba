# Script to force an xml to be multiline. Dirty but useful for debug.
input = "scene_fbx.xml"
output= "scene_fbx_multiline.xml"

inputfile=open(input, encoding="utf8")
outputfile=open(output, "w", encoding="utf8")
print("Making multiline file")
for line in inputfile :
	splitted = line.split(">")
	for stuff in splitted[:-1] :
		outputfile.write(stuff+">\n")
	outputfile.write(splitted[-1])
print("Done")
inputfile.close()
outputfile.close()
