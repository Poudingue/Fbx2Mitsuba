# Max2Mitsuba

A converter from 3dsmax scenes to mitsuba renderer scenes.

## Howto

- export the 3dsmax scene to ase and fbx (for now with the file name being «scene»)
- install python if you don't have it already
- use converter.py
- the mitsuba output file is «scene.xml»

## What will be converted
- Positions and fov of cameras (no tilt yet)
- Positions and intensity of lights (sphere lightsources conversion for soft shadows work)
- Meshes (separated by material for a single 3d object)
- Materials : Only Phong is correct for now
- Textures : No uv mapping for now
- Envmap : will count as a lightsource contrary to 3dsmax, so expect different lighting for the scene.

## Potential problems

- Limited to small scale scenes for now (because of intermediate xml files which are hard to handle when they get bigger)

## How it works

- ase and fbx files are converted to intermediate xml
- meshes and materials from the converted ase file. Vertex normal depend on the face using it, so I duplicated vertex to store different normals for each face.
- If an object has multiple materials applied to it, it will create a separate mesh for each one.
- Materials are stored in a separate folder
- The scene is generated from the intermediate files, as well as the meshes generated.

## Copyright and stuff

Please understand that this is an experimental ongoing project, so the code might be hard to understand, and some unexpected problems might occur.

Right now, you can use my (unfinished) work, but i'm not responsible if anything goes wrong.
So, use at your own risks, be responsible, fasten your seatbelts, and drive safely.
