# Fbx2Mitsuba

A converter from fbx (3dsmax exported scenes) to mitsuba renderer scenes.

## Howto

- export the 3dsmax scene to “scene.fbx” (ascii fbx, not binary !)
- install python 3.7 if you don't have it already
- install Pillow for Python (used for roughness map conversion)
- use converter.py (double click on it if you don't know how)
- available commands :
	- --verbose (or -v) displays more info about conversion
	- --debug (or -d) exports all fbx infos to an xml file (scene_fbx.xml) ⚠️Can take a very long time for big files⚠️
 	- --realist and --closest allow to choose between the most realistic rendering or the more faithful to the original 3dsmax. If you don't know don't put any, it will achieve a “balanced” look
	- --portable uses relative file path for textures, useful if you intend to transfer your scene to another computer
- the mitsuba output file is “scene.xml”

## What will be converted

- Target cameras
- Positions, colors and intensity of lights (sphere lights correctly taken into account)
- Meshes (separated by material for a single 3d object)
- Materials : Should work pretty well with 3dsmax's “physical” materials.
- Textures should work for diffuse, roughness and bumpmapping, with uv mapping.
	- If a texture reference is not found, the texture will be replaced with a default error texture

## What won't be converted

### Should be fixed soon

- Other cameras
- Background color/light
- Colored specular
- Some bumpmap seem to be referencing other textures. Investigate.
- Some advanced texture-based characteristics are not yet supported
- Object depending on a hierarchy won't be included in the final scene (yet), to avoid problems with placement.

### Harder to fix, will try anyway

- Non pointlight light types are not included
- Translucent materials

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

The source code is intended to be viewed with a 4 space indentation
Please understand that this is an experimental ongoing project, some unexpected problems might occur.

Right now, you can use my (unfinished) work, but i'm not responsible if anything goes wrong.
However, right now it's under WTFPL license.
So, use at your own risks, be responsible, fasten your seatbelts, and drive safely.
