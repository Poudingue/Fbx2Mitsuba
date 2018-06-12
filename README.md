# ASE2Mitsuba

A conversion from 3Dsmax to the Mitsuba renderer.
My approach for now is to export in ASE (Ascii Scene Export), and convert as much info as possible into a Mitsuba renderer file.

ase2xml.py can be used to convert the ase into xml.
fbx2xml.py does the same from an fbx file.
Both seem to work well, tell me if there is any problem with the output xml files

plybuilder exports meshes from the ase scene. Does not include texture or vertex normal yet.

asexml2mitsubaxml.py can be used to convert this new xml into a mitsuba scene xml (incomplete, does not include geometry)

asexml2mitsubaxmlexperimental.py uses the fbx file to extract the radii of different lights. Dirty workaround for now.
It also uses the files created by plybuilder for the geometry.


mesh2obj.py doesn't work either, its goal is to export the mesh from ase to obj or ply files. Not sure yet which one.
