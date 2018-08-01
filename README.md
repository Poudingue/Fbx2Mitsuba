# Fbx2Mitsuba

A converter from fbx (3dsmax exported scenes) to mitsuba renderer scenes.

## Howto

- export the 3dsmax scene to “scene.fbx” (ascii fbx, not binary !)
- install python if you don't have it already
- use converter.py (double)
- available commands :
	- --verbose (or -v) displays more info about conversion
	- --debug (or -d) exports all fbx infos to an xml file (scene_fbx.xml) ⚠️Can take a long time for big files⚠️
 	- --realist and --closest allow to choose between the most realistic rendering or the more faithful to the original 3dsmax. If you don't know don't put any, it will achieve a “balanced” look
	- --portable uses relative file path for textures, useful if you intend to transfer your scene to another computer
- the mitsuba output file is “scene.xml”

## What will be converted

- SOME cameras
- Positions, colors and intensity of lights (sphere lights correctly taken into account)
- Meshes (separated by material for a single 3d object)
- Materials : Only Phong is correct for now. Other ones may not be correctly rendered
- Textures should work for diffuse, with uv mapping.

## What won't be converted

### Should be fixed soon

- Background color/light
- Normal, bumpmapping, and any textured caracteristic which is not diffuse are not yet supported
- Some cameras won't be transfered because… Because reasons.
- Object depending on a hierarchy won't be included in the final scene (yet), to avoid problems with placement.

### Harder to fix, will try anyway

- Non pointlight light types are not included

### Probably unfixable

- Particle systems and effects. For obvious reasons.
- Materials :
	- Self-illumination based on texture
	- So called “Raytrace” 3dsmax material may never be supported. Those material are not even supported by 3dsmax raytracing methods.
	- The “Metal” shader either, because it doesn't correspond to anything standard and is not supported by 3dsmax raytracing methods.
- Reference to environnment map do not seem to be included in the fbx file. Will maybe add an option to force envmap.


## How it works

- FBX file is parsed (and written to xml file if debug is active)
- lights and cameras are added to the scene
- every texture is referenced with a unique id
- every material is referenced with a unique id, and can use textures id
- every 3d object create a shapegroup, containing all the geometry, with a unique id
	- if an object has multiple materials applied to it, it will create a separate mesh for each one
- every object placed on the scene create a shape, referencing shapegroups, correctly placed, scaled and rotated.
- meshes are stored in their respective folder
- everything is written in the “scene.xml” file, except for meshes, staying in their respective folder

## Roadmap

- Shorten and simplify code
- Increase the number of supported materials
- More parameters
- More type of lights support
- More cameras support
- Texture tiling support
- Catch more potential problem with fbx file infos

## Copyright and stuff

Please understand that this is an experimental ongoing project, so the code might be ugly, and some unexpected problems might occur.

Right now, you can use my (unfinished) work, but i'm not responsible if anything goes wrong.
So, use at your own risks, be responsible, fasten your seatbelts, and drive safely.
