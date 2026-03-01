import json
import math
import maya.cmds as cmds

# ─────────────────────────────────────────────────────────────────────────────
# SHADER NODE REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
NODE_REGISTRY = {
    "file": {
        "blenderType": "ShaderNodeTexImage",
        "inputs":  {"uvCoord": "Vector"},
        "outputs": {"outColor": "Color", "outAlpha": "Alpha", "outColorR": "Color"},
        "attrs":   ["fileTextureName", "uvTilingMode", "colorSpace", "alphaIsLuminance"],
    },
    "place2dTexture": {
        "blenderType": "ShaderNodeMapping",
        "inputs":  {},
        "outputs": {"outUV": "Vector"},
        "attrs":   ["repeatU", "repeatV", "offsetU", "offsetV", "rotateUV", "wrapU", "wrapV"],
    },
    "bump2d": {
        "blenderType": "ShaderNodeBump",
        "inputs":  {"bumpValue": "Height"},
        "outputs": {"outNormal": "Normal"},
        "attrs":   ["bumpDepth", "bumpInterp"],
    },
    "aiNormalMap": {
        "blenderType": "ShaderNodeNormalMap",
        "inputs":  {"input": "Color"},
        "outputs": {"outValue": "Normal"},
        "attrs":   ["strength", "colorSpace"],
    },
    "multiplyDivide": {
        "blenderType": "ShaderNodeMath",
        "inputs":  {"input1X": "Value", "input2X": "Value",
                    "input1": "Value", "input2": "Value"},
        "outputs": {"outputX": "Value", "output": "Value"},
        "attrs":   ["operation",
                    "input1X", "input1Y", "input1Z",
                    "input2X", "input2Y", "input2Z"],
    },
    "addDoubleLinear": {
        "blenderType": "ShaderNodeMath", "blenderSubtype": "ADD",
        "inputs":  {"input1": "Value", "input2": "Value"},
        "outputs": {"output": "Value"},
        "attrs":   ["input1", "input2"],
    },
    "multDoubleLinear": {
        "blenderType": "ShaderNodeMath", "blenderSubtype": "MULTIPLY",
        "inputs":  {"input1": "Value", "input2": "Value"},
        "outputs": {"output": "Value"},
        "attrs":   ["input1", "input2"],
    },
    "unitConversion": {
        "blenderType": "ShaderNodeMath", "blenderSubtype": "MULTIPLY",
        "inputs":  {"input": "Value"},
        "outputs": {"output": "Value"},
        "attrs":   ["conversionFactor"],
    },
    "aiAbs": {
        "blenderType": "ShaderNodeMath", "blenderSubtype": "ABSOLUTE",
        "inputs":  {"input": "Value"},
        "outputs": {"outValue": "Value"},
        "attrs":   [],
    },
    "vectorProduct": {
        "blenderType": "ShaderNodeVectorMath",
        "inputs":  {"input1": "Vector", "input2": "Vector"},
        "outputs": {"output": "Vector"},
        "attrs":   ["operation", "normalizeOutput"],
    },
    "blendColors": {
        "blenderType": "ShaderNodeMixRGB", "blenderSubtype": "MIX",
        "inputs":  {"color1": "Color1", "color2": "Color2", "blender": "Fac"},
        "outputs": {"output": "Color"},
        "attrs":   ["blender"],
    },
    "layeredTexture": {
        "blenderType": "ShaderNodeMixRGB", "blenderSubtype": "MIX",
        "inputs":  {},
        "outputs": {"outColor": "Color"},
        "attrs":   [],
    },
    "aiMultiply": {
        "blenderType": "ShaderNodeMixRGB", "blenderSubtype": "MULTIPLY",
        "inputs":  {"input1": "Color1", "input2": "Color2"},
        "outputs": {"outColor": "Color"},
        "attrs":   ["input1", "input2"],
    },
    "aiAdd": {
        "blenderType": "ShaderNodeMixRGB", "blenderSubtype": "ADD",
        "inputs":  {"input1": "Color1", "input2": "Color2"},
        "outputs": {"outColor": "Color"},
        "attrs":   [],
    },
    "aiSubtract": {
        "blenderType": "ShaderNodeMixRGB", "blenderSubtype": "SUBTRACT",
        "inputs":  {"input1": "Color1", "input2": "Color2"},
        "outputs": {"outColor": "Color"},
        "attrs":   [],
    },
    "aiMix": {
        "blenderType": "ShaderNodeMixRGB", "blenderSubtype": "MIX",
        "inputs":  {"input1": "Color1", "input2": "Color2", "mix": "Fac"},
        "outputs": {"outColor": "Color"},
        "attrs":   ["mix"],
    },
    "gammaCorrect": {
        "blenderType": "ShaderNodeGamma",
        "inputs":  {"value": "Color", "gammaX": "Gamma"},
        "outputs": {"outValue": "Color"},
        "attrs":   ["gammaX"],
    },
    "clamp": {
        "blenderType": "ShaderNodeClamp",
        "inputs":  {"inputR": "Value"},
        "outputs": {"outputR": "Result"},
        "attrs":   ["minR", "maxR"],
    },
    "reverse": {
        "blenderType": "ShaderNodeInvert",
        "inputs":  {"input": "Color"},
        "outputs": {"output": "Color"},
        "attrs":   [],
    },
    "luminance": {
        "blenderType": "ShaderNodeRGBToBW",
        "inputs":  {"value": "Color"},
        "outputs": {"outValue": "Val"},
        "attrs":   [],
    },
    "hsvToRgb": {
        "blenderType": "ShaderNodeHueSaturation",
        "inputs":  {"inHsv": "Color"},
        "outputs": {"outRgb": "Color"},
        "attrs":   [],
    },
    "aiColorCorrect": {
        "blenderType": "ShaderNodeHueSaturation",
        "inputs":  {"input": "Color"},
        "outputs": {"outColor": "Color"},
        "attrs":   ["hueOffset", "saturation", "contrast", "exposure", "gamma"],
    },
    "ramp": {
        "blenderType": "ShaderNodeValToRGB",
        "inputs":  {"uvCoord": "Fac"},
        "outputs": {"outColor": "Color", "outAlpha": "Alpha"},
        "attrs":   ["__rampEntries__", "interpolation", "type"],
    },
    "noise": {
        "blenderType": "ShaderNodeTexNoise",
        "inputs":  {"uvCoord": "Vector"},
        "outputs": {"outColor": "Color"},
        "attrs":   ["frequency", "amplitude", "ratio", "frequencyRatio", "depth", "time"],
    },
    "fractal": {
        "blenderType": "ShaderNodeTexNoise",
        "inputs":  {"uvCoord": "Vector"},
        "outputs": {"outColor": "Color"},
        "attrs":   ["amplitude", "frequencyRatio", "time"],
    },
    "aiMixShader": {
        "blenderType":    "ShaderNodeMixRGB",
        "blenderSubtype": "MIX",
        "inputs":  {"shader1": "Color1", "shader2": "Color2", "mix": "Fac"},
        "outputs": {"outColor": "Color"},
        "attrs":   ["mix"],
    },
}

MULTIPLY_DIVIDE_OPS = {1: "MULTIPLY", 2: "DIVIDE", 3: "POWER"}
VECTOR_PRODUCT_OPS  = {0: "DOT_PRODUCT", 1: "CROSS_PRODUCT",
                       2: "VECTOR_MATRIX_PRODUCT", 3: "POINT_MATRIX_PRODUCT"}

AI_STD_ATTRS = [
    "baseColor", "metalness", "specular", "specularRoughness",
    "subsurface", "subsurfaceColor", "subsurfaceRadius",
    "transmission", "emission", "emissionColor", "coat", "coatRoughness",
    "normalCamera", "opacity",
]

# ─────────────────────────────────────────────────────────────────────────────
# LIGHT REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

LIGHT_TYPE_MAP = {
    "pointLight":       "POINT",
    "spotLight":        "SPOT",
    "directionalLight": "SUN",
    "areaLight":        "AREA",
    "aiAreaLight":      "AREA",
    "aiSkyDomeLight":   "WORLD",
}

COMMON_LIGHT_ATTRS = [
    "aiDiffuse", "aiSpecular", "aiSss", "aiIndirect", "aiVolume",
    "aiMaxBounces", "aiCastShadows", "aiCastVolumetricShadows",
    "aiShadowDensity", "aiShadowColor", "aiSamples", "aiNormalize",
]

LIGHT_EXTRA_ATTRS = {
    "pointLight":       ["aiRadius"],
    "spotLight":        ["coneAngle", "penumbraAngle", "dropoff", "aiRadius"],
    "directionalLight": ["aiAngle"],
    "areaLight":        ["aiSpread", "aiRoundness", "aiSoftEdge"],
    "aiAreaLight":      ["aiSpread", "aiRoundness", "aiSoftEdge"],
    "aiSkyDomeLight":   ["aiFormat", "aiPortalMode",
                         "aiAovIndirectDiffuse", "aiAovIndirectSpecular"],
}


# ─────────────────────────────────────────────────────────────────────────────
# Shader helpers
# ─────────────────────────────────────────────────────────────────────────────

def safe_get(node, attr):
    try:
        if not cmds.attributeQuery(attr, node=node, exists=True):
            return None
        val = cmds.getAttr(f"{node}.{attr}")
        if isinstance(val, list) and len(val) == 1:
            val = val[0]
        if isinstance(val, tuple):
            val = list(val)
        return val
    except Exception:
        return None


def export_ramp_entries(node):
    entries = []
    indices = cmds.getAttr(f"{node}.colorEntryList", multiIndices=True) or []
    for i in indices:
        pos = safe_get(node, f"colorEntryList[{i}].colorPosition")
        col = safe_get(node, f"colorEntryList[{i}].color")
        if pos is not None and col is not None:
            entries.append({
                "position": pos,
                "color": list(col) if isinstance(col, (list, tuple)) else col,
            })
    return entries


def traverse_graph(start_plug, visited, nodes_out):
    conns = cmds.listConnections(
        start_plug, plugs=True, source=True, destination=False
    ) or []
    if not conns:
        return None
    src_plug  = conns[0]
    node      = src_plug.split('.')[0]
    node_type = cmds.nodeType(node)

    if node not in visited:
        visited.add(node)
        info      = NODE_REGISTRY.get(node_type)
        supported = info is not None
        entry = {
            "mayaType":       node_type,
            "blenderType":    info["blenderType"] if supported else None,
            "blenderSubtype": info.get("blenderSubtype") if supported else None,
            "inputMap":       info["inputs"]  if supported else {},
            "outputMap":      info["outputs"] if supported else {},
            "supported":      supported,
            "attributes":     {},
            "connections":    {},
        }
        if supported:
            for attr in info["attrs"]:
                if attr == "__rampEntries__":
                    entry["attributes"]["rampEntries"] = export_ramp_entries(node)
                    continue
                val = safe_get(node, attr)
                if val is not None:
                    entry["attributes"][attr] = val
            if node_type == "multiplyDivide":
                op = safe_get(node, "operation")
                entry["blenderSubtype"] = MULTIPLY_DIVIDE_OPS.get(op, "MULTIPLY")
            elif node_type == "vectorProduct":
                op = safe_get(node, "operation")
                entry["blenderSubtype"] = VECTOR_PRODUCT_OPS.get(op, "DOT_PRODUCT")
            elif node_type == "file":
                entry["attributes"]["udim"] = (safe_get(node, "uvTilingMode") == 3)
            for maya_input in info["inputs"]:
                src = traverse_graph(f"{node}.{maya_input}", visited, nodes_out)
                if src:
                    entry["connections"][maya_input] = src
            if node_type == "multiplyDivide":
                for base in ["input1", "input2"]:
                    for comp in ["X", "Y", "Z"]:
                        attr = f"{base}{comp}"
                        src = traverse_graph(f"{node}.{attr}", visited, nodes_out)
                        if src:
                            entry["connections"][attr] = src
        nodes_out[node] = entry
    return src_plug


def build_shader_graph(shader):
    visited = set()
    nodes   = {}
    inputs  = {}
    for attr in AI_STD_ATTRS:
        src = traverse_graph(f"{shader}.{attr}", visited, nodes)
        if src:
            inputs[attr] = src
        else:
            val = safe_get(shader, attr)
            if val is not None:
                inputs[attr] = {"value": val}
    return {"nodes": nodes, "inputs": inputs}


# ─────────────────────────────────────────────────────────────────────────────
# Light helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_light_color(shape):
    raw = safe_get(shape, "color")
    if raw is None:
        return [1.0, 1.0, 1.0]
    if isinstance(raw, (list, tuple)):
        flat = raw[0] if (len(raw) == 1 and isinstance(raw[0], (list, tuple))) else raw
        return [float(flat[0]), float(flat[1]), float(flat[2])]
    return [1.0, 1.0, 1.0]


def get_skydome_texture(shape):
    conns = cmds.listConnections(
        f"{shape}.color", plugs=True, source=True, destination=False
    ) or []
    for conn in conns:
        node  = conn.split('.')[0]
        ntype = cmds.nodeType(node)
        if ntype == "file":
            return safe_get(node, "fileTextureName")
        sub = cmds.listConnections(
            f"{node}.color", plugs=True, source=True, destination=False
        ) or []
        for sc in sub:
            sn = sc.split('.')[0]
            if cmds.nodeType(sn) == "file":
                return safe_get(sn, "fileTextureName")
    return None


def export_light(shape, light_type):
    transform = cmds.listRelatives(shape, parent=True, fullPath=True)[0]

    translate = cmds.xform(transform, q=True, worldSpace=True, translation=True)
    rotate    = cmds.xform(transform, q=True, worldSpace=True, rotation=True)
    scale     = cmds.xform(transform, q=True, worldSpace=True, scale=True)

    intensity      = float(safe_get(shape, "intensity") or 1.0)
    exposure       = float(safe_get(shape, "aiExposure") or 0.0)
    use_color_temp = bool(safe_get(shape, "aiUseColorTemperature") or False)
    color_temp     = float(safe_get(shape, "aiColorTemperature") or 6500.0)

    entry = {
        "mayaType":     light_type,
        "blenderType":  LIGHT_TYPE_MAP[light_type],
        "transform": {
            "translate": list(translate),
            "rotate":    list(rotate),
            "scale":     list(scale),
        },
        "intensity":    intensity,
        "exposure":     exposure,
        "useColorTemp": use_color_temp,
        "colorTemp":    color_temp,
        "color":        get_light_color(shape),
        "attributes":   {},
    }

    for attr in COMMON_LIGHT_ATTRS:
        val = safe_get(shape, attr)
        if val is not None:
            entry["attributes"][attr] = val

    for attr in LIGHT_EXTRA_ATTRS.get(light_type, []):
        val = safe_get(shape, attr)
        if val is not None:
            entry["attributes"][attr] = val

    if light_type in ("areaLight", "aiAreaLight"):
        entry["attributes"]["blenderSizeX"] = abs(scale[0]) * 10.0
        entry["attributes"]["blenderSizeY"] = abs(scale[1]) * 10.0

    if light_type == "spotLight":
        cone   = float(safe_get(shape, "coneAngle")    or 40.0)
        penumb = float(safe_get(shape, "penumbraAngle") or 0.0)
        outer  = cone + 2.0 * max(penumb, 0.0)
        blend  = ((2.0 * max(penumb, 0.0)) / outer) if outer > 0 else 0.0
        entry["attributes"]["blenderSpotSize"]  = math.radians(outer)
        entry["attributes"]["blenderSpotBlend"] = min(max(blend, 0.0), 1.0)

    if light_type == "directionalLight":
        entry["attributes"]["blenderAngle"] = math.radians(
            float(safe_get(shape, "aiAngle") or 0.526)
        )

    if light_type == "aiSkyDomeLight":
        entry["attributes"]["hdriPath"] = get_skydome_texture(shape)

    return transform, entry


# ─────────────────────────────────────────────────────────────────────────────
# Main export
# ─────────────────────────────────────────────────────────────────────────────

def export_ai_standard_surface_data():
    # Step 1 — scope
    scope = cmds.confirmDialog(
        title="Export Scope",
        message="Export all objects or selected objects only?",
        button=["All", "Selected", "Cancel"],
        defaultButton="All",
        cancelButton="Cancel",
        dismissString="Cancel",
    )
    if scope == "Cancel":
        cmds.warning("Export cancelled.")
        return
    export_selected = (scope == "Selected")

    # Step 2 — frame range
    start_frame = int(cmds.playbackOptions(q=True, minTime=True))
    end_frame   = int(cmds.playbackOptions(q=True, maxTime=True))
    range_result = cmds.promptDialog(
        title="Frame Range",
        message=f"Frame range (start end):",
        text=f"{start_frame} {end_frame}",
        button=["OK", "Cancel"],
        defaultButton="OK",
        cancelButton="Cancel",
        dismissString="Cancel",
    )
    if range_result == "Cancel":
        cmds.warning("Export cancelled.")
        return
    try:
        parts = cmds.promptDialog(query=True, text=True).split()
        if len(parts) == 1:
            start_frame = end_frame = int(parts[0])
        else:
            start_frame, end_frame = int(parts[0]), int(parts[1])
    except Exception:
        cmds.warning("Invalid frame range — using timeline defaults.")

    # Step 3 — pick save path (Alembic)
    path = cmds.fileDialog2(
        fileMode=0,
        caption="Save Alembic",
        fileFilter="Alembic Files (*.abc)",
    )
    if not path:
        cmds.warning("Export cancelled.")
        return
    abc_path = path[0]
    if not abc_path.lower().endswith(".abc"):
        abc_path += ".abc"

    # Step 4 — export Alembic
    # -uvWrite        : export UV sets
    # -worldSpace     : bake transforms to world space (matches JSON light positions)
    # -writeVisibility: carry visibility flags
    # -dataFormat ogawa: modern compact format (vs HDF5)
    if export_selected:
        roots = cmds.ls(selection=True, long=True)
        if not roots:
            cmds.warning("Nothing selected.")
            return
        root_flags = " ".join(f"-root {r}" for r in roots)
        job = (f"-frameRange {start_frame} {end_frame} "
               f"-uvWrite -worldSpace -writeVisibility -dataFormat ogawa "
               f"{root_flags} -file {abc_path}")
    else:
        job = (f"-frameRange {start_frame} {end_frame} "
               f"-uvWrite -worldSpace -writeVisibility -dataFormat ogawa "
               f"-file {abc_path}")

    cmds.AbcExport(j=job)
    print("[INFO] Alembic exported -> " + abc_path)

    # Step 5 — collect shader & light data
    json_path   = abc_path[:-4] + ".json"
    export_data = {"meshes": {}, "shaders": {}, "lights": {}}

    # Collect meshes — store the full DAG path so the importer can match
    # on the leaf name even inside deeply nested hierarchies.
    # Collect display layers: name → {visible, objects}
    # "defaultLayer" is Maya's built-in catch-all — skip it.
    layers_data = {}
    for layer in cmds.ls(type="displayLayer") or []:
        if layer == "defaultLayer":
            continue
        layer_vis  = bool(cmds.getAttr(layer + ".visibility"))
        layer_objs = cmds.editDisplayLayerMembers(layer, q=True, fullNames=True) or []
        layers_data[layer] = {
            "visible": layer_vis,
            "members": [o.split("|")[-1] for o in layer_objs],
        }
    export_data["layers"] = layers_data

    # Build reverse map: transform short-name → layer name
    _transform_to_layer = {}
    for layer, ldata in layers_data.items():
        for m in ldata["members"]:
            _transform_to_layer[m] = layer

    mesh_list = cmds.ls(type="mesh", noIntermediate=True)
    if export_selected:
        # Limit to meshes under the selected roots
        selected_set = set(cmds.listRelatives(
            roots, allDescendents=True, fullPath=True, type="mesh"
        ) or [])
        mesh_list = [m for m in mesh_list if m in selected_set]

    for mesh in mesh_list:
        transform     = cmds.listRelatives(mesh, parent=True, fullPath=True)[0]
        sgs           = cmds.listConnections(mesh, type="shadingEngine") or []
        # displaySmoothMesh == 2 → smooth-preview mode (key 3 in Maya)
        smooth_preview = (safe_get(mesh, "displaySmoothMesh") == 2)
        # Visibility: check the transform node (shape inherits from it)
        is_visible = bool(cmds.getAttr(transform + ".visibility"))
        transform_short = transform.split("|")[-1]
        export_data["meshes"][mesh] = {
            "transform":          transform,
            "fullPath":           transform,   # kept for hierarchy matching
            "materials":          [],
            "subdivisionPreview": smooth_preview,
            "visible":            is_visible,
            "displayLayer":       _transform_to_layer.get(transform_short),
        }
        for sg in sgs:
            surface_shaders = cmds.listConnections(
                sg + ".surfaceShader", type="aiStandardSurface"
            ) or []
            if not surface_shaders:
                continue
            shader = surface_shaders[0]
            if shader not in export_data["shaders"]:
                export_data["shaders"][shader] = build_shader_graph(shader)
            export_data["meshes"][mesh]["materials"].append(shader)

    for light_type in LIGHT_TYPE_MAP:
        for shape in cmds.ls(type=light_type) or []:
            try:
                transform, entry = export_light(shape, light_type)
                short_name = transform.split("|")[-1]
                export_data["lights"][short_name] = entry
                print("[INFO] Light: " + short_name + " (" + light_type + ")")
            except Exception as e:
                cmds.warning("Could not export light '" + shape + "': " + str(e))

    # Step 5b — collect locally-hidden transform nodes
    # In Maya, hiding a group hides all its descendants (inherited visibility).
    # Blender empties don't propagate visibility to children, so we record
    # every transform whose LOCAL visibility flag is False.  The importer will
    # walk each such node's Blender children and hide them recursively.
    hidden_transforms = []
    for t in (cmds.ls(type="transform", long=True) or []):
        try:
            if not cmds.getAttr(t + ".visibility"):
                hidden_transforms.append(t.split("|")[-1])
        except Exception:
            pass
    export_data["hiddenTransforms"] = hidden_transforms

    # Step 6 — write JSON
    try:
        with open(json_path, "w") as f:
            json.dump(export_data, f, indent=4)
        print("[INFO] JSON exported: "
              + str(len(export_data["meshes"])) + " meshes, "
              + str(len(export_data["shaders"])) + " shaders, "
              + str(len(export_data["lights"])) + " lights -> " + json_path)
    except IOError as e:
        cmds.error("Failed to write JSON: " + str(e))
        return

    msg = ("Export complete."
           + "\n\nAlembic: " + abc_path
           + "\nJSON:    " + json_path
           + "\nFrames:  " + str(start_frame) + " – " + str(end_frame))
    cmds.confirmDialog(title="Done", message=msg, button=["OK"])


export_ai_standard_surface_data()
