# Fbx2Mitsuba

A converter from 3dsmax scenes to mitsuba renderer scenes.

## Howto

- export the 3dsmax scene to scene.fbx (ascii fbx, not binary)
- install python if you don't have it already
- use converter.py . commands --verbose (-v) and --debug (-d) available)
- additionnal commands --realist and --closest allow to choose between the most realistic rendering or the more faithful to the original 3dsmax. If you don't know don't put any, it will achieve a “balanced” look
- the mitsuba output file is “scene.xml”

## What will be converted

- SOME cameras
- Positions and intensity of lights (sphere lights correctly taken into account)
- Meshes (separated by material for a single 3d object)
- Materials : Only Phong is correct for now. Other ones may not be correctly rendered
	- Normal or bumpmapping not yet supported
	- So called “Raytrace” 3dsmax material may never be supported. Those material are not even supported by 3dsmax raytracing methods.
	- The “Metal” shader either, because it doesn't correspond to anything standard and is not supported by 3dsmax raytracing methods.
- Textures :
	- Should work for diffuse use.
	- uvmapping too
- Envmap seem not to be included in the fbx file, i will try to retrieve this


## How it works

- FBX file is parsed (and written to xml file if debug is active)
- lights and cameras are added to the scene
- every texture is referenced with a unique id
- every material is referenced with a unique id, and can use textures id
- every model create a shapegroup, containing all the geometry
- if an object has multiple materials applied to it, it will create a separate mesh for each one.
- these meshes can use a material id
- meshes are stored in their respective folder
- everything is written in the “scene.xml” file, except for meshes, staying in their respective folder

## Roadmap

- Shorten and simplify code
- Increase the number of supported materials -> very soon
- More parameters
- More type of lights support
- More cameras support
- Texture tiling support -> very soon

## Currently developping

## Copyright and stuff

Please understand that this is an experimental ongoing project, so the code might be ugly, and some unexpected problems might occur.

Right now, you can use my (unfinished) work, but i'm not responsible if anything goes wrong.
So, use at your own risks, be responsible, fasten your seatbelts, and drive safely.
