# Max2Mitsuba

A converter from 3dsmax scenes to mitsuba renderer scenes.

## Howto

- export the 3dsmax scene to scene.ase and scene.fbx (ascii fbx, not binary)
- install python if you don't have it already
- use converter.py (command --verbose and --debug available)
- the mitsuba output file is «scene.xml»

## What will be converted

- Positions and fov of cameras (no tilt yet)
- Positions and intensity of lights (sphere lights correctly taken into account)
- Meshes (separated by material for a single 3d object)
- Materials : Only Blinn-Phong is correct for now. Other ones will appear as red diffuse.
	- Normal or bumpmapping not yet supported
	- So called “Raytrace” 3dsmax material may never be supported. Those material are not even supported by 3dsmax raytracing methods.
	- The “Metal” shader either, because it doesn't correspond to anything standard and is not supported by 3dsmax raytracing methods.
- Textures : basic uv mapping, may or may not work.
- Environnement map will count as a lightsource. This is a major difference compared to “Scanline” or “Metalray” rendering in 3dsmax
	- (Envmap are temporarily not working)


## How it works

- ASE and FBX files are parsed (and written to xml files if debug is active)
- if an object has multiple materials applied to it, it will create a separate mesh for each one.
- meshes are stored in their respective folder
- materials are stored in a separate folder
- The scene is generated from the intermediate files, as well as the meshes generated.
- Useless intermediate files are deleted (except if debug mode is activated)

## Roadmap

- Shorten and simplify code
- More but smaller python functions ?
- Make a faster xml prettifier
- Increase the number of supported materials
- Use the ASE file less and less, and the FBX more and more, for multiple reasons :
	- more info, contains everything we need
	- everything has a unique id (no more problems with multiple objects having the same name)
	- support for non-ascii utf8 characters (not the ase, and it causes some problems)
	- Only one file to parse instead of two
- More parameters than “verbose” and “debug” for conversion
- More type of lights support
- Free camera support
- Texture tiling support

## Copyright and stuff

Please understand that this is an experimental ongoing project, so the code might be hard to understand, and some unexpected problems might occur.

Right now, you can use my (unfinished) work, but i'm not responsible if anything goes wrong.
So, use at your own risks, be responsible, fasten your seatbelts, and drive safely.
