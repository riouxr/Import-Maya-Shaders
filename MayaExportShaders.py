import json
import maya.cmds as cmds

# List of aiStandardSurface attributes to export
AI_STD_ATTRS = [
    "baseColor", "metalness", "specular", "specularRoughness",
    "subsurface", "subsurfaceColor", "subsurfaceRadius",
    "transmission", "emissionColor", "coat", "coatRoughness"
]

def get_file_info(attribute):
    """
    Recursively follows the connection chain until finding a file node.
    Returns a dict: {"filePath": <str or None>, "udim": <bool>}
    """
    connections = cmds.listConnections(attribute, plugs=True) or []
    for conn in connections:
        node, plug = conn.split('.', 1)
        node_type = cmds.nodeType(node)
        if node_type == 'file':
            file_path = cmds.getAttr(f"{node}.fileTextureName") if cmds.attributeQuery("fileTextureName", node=node, exists=True) else None
            tile_mode = cmds.getAttr(f"{node}.uvTilingMode") if cmds.attributeQuery("uvTilingMode", node=node, exists=True) else 0
            return {"filePath": file_path, "udim": (tile_mode == 3)}
        elif node_type in ['bump2d', 'aiNormalMap']:
            return get_file_info(f"{node}.bumpValue" if node_type == 'bump2d' else f"{node}.input")
    return {"filePath": None, "udim": False}

def export_ai_standard_surface_data():
    """
    Exports meshes with their assigned aiStandardSurface shaders and shader data.
    """
    file_path = cmds.fileDialog2(fileMode=0, caption="Save Shader Data", fileFilter="JSON Files (*.json)")
    if not file_path:
        cmds.warning("Export canceled by user.")
        return

    output_path = file_path[0]
    if not output_path.lower().endswith(".json"):
        output_path += ".json"

    export_data = {"meshes": {}, "shaders": {}}

    # Collect Meshes and Assigned Materials
    for mesh in cmds.ls(type='mesh', noIntermediate=True):
        transform = cmds.listRelatives(mesh, parent=True, fullPath=True)[0]
        shading_groups = cmds.listConnections(mesh, type='shadingEngine') or []

        export_data["meshes"][mesh] = {"transform": transform, "materials": []}

        for sg in shading_groups:
            surface_shader = cmds.listConnections(sg + ".surfaceShader", type="aiStandardSurface") or []
            if not surface_shader:
                continue
            shader = surface_shader[0]

            if shader not in export_data["shaders"]:  # Avoid duplicates
                export_data["shaders"][shader] = {"textures": {}, "values": {}}

                # Get shader attributes and connected textures
                for attr in AI_STD_ATTRS:
                    file_info = get_file_info(f"{shader}.{attr}")
                    if file_info["filePath"]:
                        export_data["shaders"][shader]["textures"][attr] = file_info
                    elif cmds.attributeQuery(attr, node=shader, exists=True):
                        raw_value = cmds.getAttr(f"{shader}.{attr}")
                        if isinstance(raw_value, (list, tuple)) and len(raw_value) == 1:
                            raw_value = raw_value[0]
                        export_data["shaders"][shader]["values"][attr] = raw_value

            # Store shader assignment for the mesh
            export_data["meshes"][mesh]["materials"].append(shader)

    # Save to JSON file
    try:
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=4)
        print(f"Shader data successfully exported to {output_path}")
    except IOError as e:
        cmds.error(f"Failed to save the file: {e}")

# Run the function
export_ai_standard_surface_data()
