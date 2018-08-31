# User Manual

## Intro

This program transforms a 3ds Max scene into a Mitsuba Renderer scene. If you respect the step by step guide, you should obtain a Mitsuba Renderer XML file containing a scene faithful to the original.

Keep in mind that in its current state, the program does not convert anything. Materials may have wrong appearances, lights and cameras can be misplaced or missing, and multiple other problems may occur. Part of these problems will be fixed in future versions of the program, but for now, if you want to ensure a good conversion, multiple criteria are to be respected in order to maximize fidelity to the original scene.

## 3D scene prerequisites

- Lights must be photometric, either spotlight or omnidirectional. Omnidirectional lights can emit from a sphere.

- All cameras must be target cameras. Physical cameras won't be converted.
- Lights and cameras should be at the root of the hierarchy, or their placement in space may be incorrect.
- Materials must be Physical materials. Anisotropy and subsurface scattering are not yet taken into account.

- Procedural 3ds Max textures should be avoided, use bitmap textures instead.

## Steps

- Make sure you have Python 3 installed. If it's not the case or you're not sure, you can download it on the official website : https://www.python.org/
- Ensure your scene meets the prerequisites above as much as possible.
- Export your scene to the FBX format. In the export window, under “Advanced options” and “FBX file format”, select the “ASCII” type format. Don't change other options, it may cause some compatibility issues with the program.
- You can launch the conversion by simply drag and dropping your FBX file on the launcher.bat file.

## Résults

If nothing went wrong, the console should have closed automatically, and a folder named “export” should have appeared along your FBX file. This folder contains the Mitsuba Renderer scene, as well as two folders, one containing the meshes, and the other one the textures. If you want to move the scene, be sure to move the entirety of the export folder.