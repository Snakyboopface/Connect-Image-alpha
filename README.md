# Connect-Image-alpha
Have you ever imported a TON of assets only to find that the alpha isn't connected, leaving annoying black spots everywhere?

Well with this Blender addon you can easily connect the 'Alpha' of image textures to the principled BSDF shader node for all active materials within a selected collection.

Set labels for the program to prioritise, for example put "alpha" for the program to prioritise connecting image textures with a label containing "alpha" to the principled BSDF, you can also set a label to prioritise which BSDF node to connect to.
The addon will ignore letter case so if you put "alpha" nodes labeled "Alpha", for example, will still be prioritised

If no input is provided then the addon will, by default, prioritise nodes labeled:
-  "alpha" for connecting the "color" output of the image to the "alpha" of the shader
-  "color", "colour", "base colour", and "base color" for connecting the "alpha" output of the image to "alpha" input of the shader
-  and "mane" for determining which shader to connect to

