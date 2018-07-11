inputfile = open("scene_ase.xml", "r", encoding="utf8")
outputfile = open("scene_ase_out.xml", "w", encoding="utf8")

for line in inputfile :
	splitted = line.split(">")
	for stuff in splitted[:-1] :
		outputfile.write(stuff+">\n")
	outputfile.write(splitted[-1]+"\n")
print("Done")
