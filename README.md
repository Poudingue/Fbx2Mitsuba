# ASE2Mitsuba

A conversion from 3Dsmax to the Mitsuba renderer.
My approach for now is to export in ASE (Ascii Scene Export), and convert as much info as possible into a Mitsuba renderer file.

ase2xml.py can be used to convert the ase into xml.
fbx2xml.py does the same from an fbx file.
Both seem to work well, tell me if there is any problem with the output xml files

plybuilder exports ply meshes from the ase scene. Does not include materials yet.
Vertex normal depend on the face calling it, so i created duplicate vertex to store different normals.
In the future, i'll maybe export different meshes for faces concerned by different materials.

asexml2mitsubaxml.py can be used to create the scene from the xml generated from the fbx and ase, as well as the meshes generated from plybuilder.
Right now there are no materials, and may be some bugs.
