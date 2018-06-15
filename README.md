# Max2Mitsuba

A converter from 3dsmax scenes to mitsuba renderer scenes.

## Howto

- export the 3dsmax scene to ase and fbx (for now with the file name being «simplecube»)
- install python if you don't have it already
- use ase2xml and fbx2xml
- use plybuilder
- use asexml2mitsubaxml
- the mitsuba output file is «simplecubemitsuba.xml»
- the meshes folder must be present to have geometry in the scene

## What will be converted
- Positions and fov of cameras (no tilt yet)
- Positions and intensity of lights (sphere lightsources conversion for soft shadows work)
- Meshes (separated by material for a single 3d object)
- Materials : Only Phong is correct for now
- Textures : No uv mapping for now
- Envmap : will count as a lightsource contrary to 3dsmax, so expect different lighting for the scene.

## How it works

- ase2xml.py converts ase files into xml files.
- fbx2xml.py does the same for fbx files.
Both seem to work well, tell me if there is any problem with the output xml files

- plybuilder exports meshes and materials from the converted ase file
Vertex normal depend on the face using it, so I duplicated vertex to store different normals for each face.
If an object has multiple materials applied to it, it will create a separate mesh for each one.

- asexml2mitsubaxml.py creates the scene from the xml generated from the fbx and ase, as well as the meshes generated from plybuilder.

## Copyright and stuff

Right now, you can use my (unfinished) work, but i'm not responsible if anything goes wrong.
So, use at your own risks, be responsible, and please credit me if you use it in another project :)
