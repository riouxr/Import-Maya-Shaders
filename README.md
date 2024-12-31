# Import-Maya-Shaders

This is a two part process that will allow you to convert Maya aiStandradShader to PrincipalBSDF.

First, you will need Maya to export the geometry as an FBX file so that you can import it in Blender.
To export the shader descrition, you need to run the MayaExportShader.py in Maya's script editor. A file browser window will pop up so you can save your file where you want it.

In Blender, after installing the addon (import_maya_shader.zip), you will need to first import the FBX file using the default Blender FBX import addon. Then go to file, import, import Maya shader (json). This will open a file browser. Select the json file you have just exported from Maya. That's it. The shaders will be converted from aiStandardSurface to Principal BSDF.

This will only convert basic shader trees. If the Maya shader uses anything else than file inputs, like addMix, ramps, curves or any other nodes, it will not convert properly. It will only convert aiStandardSurface shaders. If there are no file input, it will take whatever value is set on the shader, including RGB information.

You can also watch this tutorial: https://youtu.be/BMMMBFw-z3Y

Special thanks to Tinkerboi for his contribution
