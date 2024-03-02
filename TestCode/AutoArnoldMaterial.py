import maya.cmds as cmds


def create_arnold_material(material,texture_node):

    keyword = "BaseColor"
    if keyword.lower() in texture_node.lower():
        cmds.connectAttr(texture_node + ".outColor", material + ".baseColor")

    keyword = "MetalNess"
    if keyword.lower() in texture_node.lower():
        cmds.setAttr(texture_node + '.colorSpace', "Raw", type='string')
        cmds.connectAttr(texture_node + ".outAlpha", material + ".metalness")

    keyword = "Roughness"
    if keyword.lower() in texture_node.lower():
        cmds.setAttr(texture_node + '.colorSpace', "Raw", type='string')
        cmds.connectAttr(texture_node + ".outAlpha", material + ".diffuseRoughness")

    keyword = "Normal"
    if keyword.lower() in texture_node.lower():
        cmds.setAttr(texture_node + '.colorSpace', "Raw", type='string')
        bump_node = cmds.createNode("bump2d")
        cmds.setAttr(bump_node + ".bumpInterp",1)
        cmds.connectAttr(bump_node + ".outNormal",material + ".normalCamera")
        cmds.connectAttr(texture_node + ".outAlpha", bump_node + ".bumpValue")

    keyword = "Opacity"
    if keyword.lower() in texture_node.lower():
        cmds.setAttr(texture_node + '.colorSpace', "Raw", type='string')
        cmds.connectAttr(texture_node + ".outAlpha", material + ".transmission")

    return material


def create_materials_from_selected_textures():

    selected_nodes = cmds.ls(sl=True)
    # create the material
    parts = selected_nodes[0].split("_")
    nameOfM = parts[1]
    material = cmds.shadingNode("aiStandardSurface", asShader=True,name=nameOfM)
    if not selected_nodes:
        cmds.warning("please select textures")
        return

    # connect the texture to material
    for texture_node in selected_nodes:
        material = create_arnold_material(material,texture_node)


# run the script
create_materials_from_selected_textures()
