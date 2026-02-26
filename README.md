# Maya Arnold → Blender Exporter/Importer

A two-part tool for transferring Arnold-shaded Maya scenes into Blender (Cycles). It exports an FBX for geometry and a JSON file for shader and light data, then reconstructs the materials and lights inside Blender.

---

## Requirements

- **Maya** with Arnold (mtoa)
- **Blender 4.5+** (tested on Blender 5.0)
- Cycles render engine

---

## Export from Maya

1. Open `MayaExportShaders_ArnoldOnly.py` in Maya's Script Editor and run it.
2. A dialog asks whether to export **All** objects or **Selected** only.
3. A file browser opens — choose a destination and filename for the `.fbx`.
4. The script exports the FBX, then writes a `.json` file with the same name in the same folder.

Both files are required for the Blender import.

---

## Import into Blender

1. Install the `import_maya_shader` addon (`Edit → Preferences → Add-ons → Install`).
2. Go to `File → Import → Maya Scene (.fbx + .json)`.
3. Navigate to and select the `.json` file — the addon will automatically find and import the paired `.fbx` first, then apply all materials and lights on top.

---

## What gets transferred

**Shaders**
- aiStandardSurface — Base Color, Metallic, Roughness, Specular, Transmission, Emission, Coat, Subsurface, Normal, Opacity
- Texture maps with UDIM support
- UV placement (repeat, offset, rotation)
- Shader networks built from supported utility nodes (see list below)

**Lights**
- Point, Spot, Directional (Sun), Area, and SkyDome (HDRI world) lights
- Intensity, exposure, color, color temperature
- Arnold-specific attributes (shadow casting, spread, radius, etc.)

**Supported utility nodes**
`file`, `place2dTexture`, `aiNormalMap`, `bump2d`, `aiMixShader`, `aiMix`, `aiMultiply`, `aiAdd`, `aiSubtract`, `aiColorCorrect`, `aiAbs`, `blendColors`, `layeredTexture`, `multiplyDivide`, `addDoubleLinear`, `multDoubleLinear`, `unitConversion`, `vectorProduct`, `ramp`, `gammaCorrect`, `clamp`, `reverse`, `luminance`, `hsvToRgb`, `noise`, `fractal`

---

## What is NOT compatible

- **Non-Arnold shaders** — only `aiStandardSurface` is supported. Lambert, Blinn, Phong, VRay, and other shader types are not exported.
- **Unsupported utility nodes** — any node in the shader graph that is not in the list above will be skipped. Inputs that depend on a skipped node will be left unconnected in Blender.
- **Procedural Arnold nodes** — `aiNoise`, `aiCellNoise`, `aiFlakes`, `aiMoirePattern`, `aiWireframe`, and similar Arnold-specific procedurals have no direct Blender equivalent and are not transferred.
- **aiMixShader with two full shaders** — when aiMixShader blends two complete aiStandardSurface networks, only the color output is mixed (via a MixRGB node). The two sub-shaders are not reconstructed as separate Principled BSDFs.
- **Geometry not supported** — NURBS surfaces, subdivision surfaces, and particles are exported as-is by Maya's FBX exporter and may not import correctly.
- **Animations and rigs** — not in scope; the exporter targets static shading and lighting only.
- **Referenced textures** — texture file paths are stored as absolute paths from the Maya machine. Textures must be manually re-linked if the Blender machine uses a different directory structure.

---

## Lighting & exposure

Maya/Arnold and Blender/Cycles calculate light intensity using different internal units, which typically causes the Blender scene to appear significantly brighter than the Maya render.

The importer applies a global scale factor to all imported light energies to compensate. This value is set near the top of `import_maya_shader.py`:

**This value will vary depending on the colour management settings active in Blender.** Filmic, AgX, and Raw all apply different tone curves that affect perceived brightness. After importing, compare a simple test render in both applications and adjust `ARNOLD_TO_BLENDER_EV` (or use Blender's scene-level exposure in `Render Properties → Color Management`) until the lighting matches.


