# ASE2Mitsuba

A conversion from 3Dsmax to the Mitsuba renderer.
My approach for now is to export in ASE (Ascii Scene Export), and convert as much info as possible into a Mitsuba renderer file.

ase2xml.py can be used to convert the ase into xml (works well)

asexml2mitsubaxml.py can be used to convert this new xml into a mitsuba scene xml (incomplete, does not include geometry)

asexml2mitsubaxmlexperimental.py uses the fbx file to extract the radii of different lights

fbx2xml.py does not work yet, and will maybe be removed.
Some extra infos need to be extracted from the fbx file, but to convert it into xml is maybe not necessary

mesh2obj.py doesn't work either, its goal is to export the mesh from ase to obj or ply files. Not sure yet which one.
