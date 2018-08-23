# Fbx2Mitsuba

A converter from FBX (3ds Max exported scenes) to Mitsuba Renderer scenes.

## Howto

- export the 3ds Max scene in the fbx format (ascii fbx, not binary !)
- install python 3.7 if you don't have it already
- install Pillow for Python (used for roughness map conversion)
- use converter.py with your fbx file as a parameter (you can drag and drop the fbx on converter.py)
- available commands :
	- --verbose (or -v) displays more info about conversion
	- --debug (or -d) exports all fbx infos to an xml file (scene_fbx.xml) ⚠️Can take a very long time for big files⚠️
 	- --realist and --closest allow to choose between the most realistic rendering or the more faithful to the original 3dsmax. If you don't know don't put any, it will achieve a “balanced” look
	- --portable uses relative file path for textures, useful if you intend to transfer your scene to another computer
- the mitsuba output file is “scene.xml”

## What will be converted

- Target cameras
- Photometric pointlights (sphere lights correctly taken into account) and spotlights
- Meshes (separated by material for a single 3d object)
	- Hierarchy of objects will be lost, but their placement should be correct
- Materials : Should work pretty well with 3dsmax's “physical” materials.
	- Metalness should work properly, with specular color based on diffuse
	- Transparency should work properly, with correct IOR and colored specular transmittance
- Textures should work for diffuse, roughness and bumpmapping, with uv mapping.
	- If a texture reference is not found, the texture will be replaced with a default error texture
	- Tiling should work properly

## What won't be converted

### Should be fixed soon

- Physical cameras
- Other photometric lights
- Background color/light
- Materials :
	- Anisotropy
	- Subsurface scattering
	- Multilayer materials
- Some bumpmap seem to be referencing other textures. Investigate.

### Harder to fix, will try anyway

- Other light types
- Other cameras

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
	- materials are called by their ids
- every object placed on the scene create a shape, referencing shapegroups, correctly placed, scaled and rotated.
- meshes are stored in their respective folder
- everything is written in the “scene.xml” file, except for meshes, staying in their respective folder

## Roadmap

- Support physical cameras
- Shorten and simplify code
- Ensure compatibility for other machines
- Make a more complete “portable” option, putting everything in a single folder
- Simplify user experience
- Documentation for users and developpers
- Increase the number of supported materials
- More parameters
- Catch more potential problem with fbx file infos

## Copyright and stuff

The source code is intended to be viewed with 4 space indentation
Please understand that this is an experimental ongoing project, some unexpected problems might occur.

Right now, you can use my (unfinished) work, but i'm not responsible if anything goes wrong.
However, right now it's under WTFPL license.
So, use at your own risks, be responsible, fasten your seatbelts, and drive safely.
