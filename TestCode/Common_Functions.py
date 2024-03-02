import maya.cmds as cmds
import Ctrl_Functions as CF
import Name_Class
def MTP(parent, child):
    # create the parentConstrain to match the child and parent
    constraint_name = cmds.parentConstraint(parent, child, maintainOffset=False)
    # delete the constraint node
    cmds.delete(constraint_name)

def check_if_Zero(obj):
    # check if the rotate values are zero
    rotateX = cmds.getAttr(obj + ".rotateX")
    rotateY = cmds.getAttr(obj + ".rotateY")
    rotateZ = cmds.getAttr(obj + ".rotateZ")

    if rotateX == 0 and rotateY == 0 and rotateZ == 0:
        return 1
    else:
        return 0

def Matrix_Paren_Constrain(parent, child):
    check_and_clear_jointOrient(child)
    # Create a multMatrix node
    name_obj = Name_Class.Name(fullname=parent)
    name_obj.type = "multMNode"
    mult_matrix_node = cmds.createNode("multMatrix", name=name_obj.fullname)

    # Connect the outputMatrix of the blendMatrix to multMatrix's matrixIn[0]
    cmds.connectAttr(parent + ".worldMatrix[0]", mult_matrix_node + ".matrixIn[0]")

    # Connect the worldInverseMatrix of the parent of the joint C to multMatrix's matrixIn[1]
    cmds.connectAttr(child + ".parentInverseMatrix[0]", mult_matrix_node + ".matrixIn[1]")

    # Create a decomposeMatrix node
    name_obj.type = "decompMNode"
    decompose_matrix_node = cmds.createNode("decomposeMatrix", name=name_obj.fullname)

    # Connect the multMatrix's matrixSum to decomposeMatrix's inputMatrix
    cmds.connectAttr(mult_matrix_node + ".matrixSum", decompose_matrix_node + ".inputMatrix")

    # Connect the decomposeMatrix's outputTranslate, outputRotate attributes to B
    cmds.connectAttr(decompose_matrix_node + ".outputTranslate", child + ".translate")
    cmds.connectAttr(decompose_matrix_node + ".outputRotate", child + ".rotate")
    return_list = [mult_matrix_node,decompose_matrix_node]

    return return_list

def Matrix_Rotation_Constrain(parent, child):
    check_and_clear_jointOrient(child)
    # Create a multMatrix node
    name_obj = Name_Class.Name(fullname=parent)
    name_obj.type = "multMNode"
    mult_matrix_node = cmds.createNode("multMatrix", name=name_obj.fullname)

    # Connect the outputMatrix of the blendMatrix to multMatrix's matrixIn[0]
    cmds.connectAttr(parent + ".worldMatrix[0]", mult_matrix_node + ".matrixIn[0]")

    # Connect the worldInverseMatrix of the parent of the joint C to multMatrix's matrixIn[1]
    cmds.connectAttr(child + ".parentInverseMatrix[0]", mult_matrix_node + ".matrixIn[1]")

    # Create a decomposeMatrix node
    name_obj.type = "decompMNode"
    decompose_matrix_node = cmds.createNode("decomposeMatrix", name=name_obj.fullname)

    # Connect the multMatrix's matrixSum to decomposeMatrix's inputMatrix
    cmds.connectAttr(mult_matrix_node + ".matrixSum", decompose_matrix_node + ".inputMatrix")

    # Connect the decomposeMatrix's outputRotate attributes to B
    cmds.connectAttr(decompose_matrix_node + ".outputRotate", child + ".rotate")
    return_list = [mult_matrix_node,decompose_matrix_node]

    return return_list

def check_and_clear_jointOrient(obj):
    # check if obj have joint orient
    if cmds.attributeQuery("jointOrientX", exists=True, node=obj) and \
            cmds.attributeQuery("jointOrientY", exists=True, node=obj) and \
            cmds.attributeQuery("jointOrientZ", exists=True, node=obj):
        # if had, then set zero to joint orient
        cmds.setAttr(obj + ".jointOrientX", 0)
        cmds.setAttr(obj + ".jointOrientY", 0)
        cmds.setAttr(obj + ".jointOrientZ", 0)

def create_Fk_ctrl(joint_name,ctrlType,degree,size,color,controller_lists):
    # get the ctrl name
    control_name = joint_name.replace("jnt_", "ctrl_")
    # create a nurbs circle nurbs
    circle=CF.createCtrl(ctrlName=control_name,ctrlType=ctrlType,degree=degree,size=size,color=color)

    # select the circle just created
    cmds.select(circle)

    # put the circle into the "circle_controllers" list
    controller_lists.append(circle)

def create_empty_group_and_match_transform(ctrl):
    # name settings
    if ctrl[:4] == "jnt_":
        group_name = ctrl.replace("jnt_", "Zero_")
    elif ctrl[:5] == "Zero_":
        group_name = ctrl.replace("Zero_", "Connect_")
    elif ctrl[:4] == "loc_":
        group_name = ctrl.replace("loc_", "Zero_")
    elif ctrl[:5] == "ctrl_":
        group_name = ctrl.replace("ctrl_", "Zero_")
    else:
        group_name = ctrl + "_Group"
    # check if have parent
    parent = cmds.listRelatives(ctrl, parent=True)

    # create a group
    empty_group = cmds.group(em=True, name=group_name)

    # match the position and axis
    cmds.matchTransform(empty_group, ctrl, pos=True, rot=True, scl=True)

    if not parent:
        # if objet don't have parent, put new group under the parent and then put object under the group
        cmds.parent(ctrl, empty_group)
    else:
        # if object have parent, put it in
        cmds.parent(empty_group, parent[0])
        cmds.parent(ctrl, empty_group)

    return empty_group

def connect_RotateAttr(ctrl, joint):
    # connect the rotate from control to joint
    cmds.connectAttr(ctrl + ".rotate.rotateX", joint + ".rotate.rotateX")
    cmds.connectAttr(ctrl + ".rotate.rotateY", joint + ".rotate.rotateY")
    cmds.connectAttr(ctrl + ".rotate.rotateZ", joint + ".rotate.rotateZ")

def bake_Rotation(obj):
    tempRX = cmds.getAttr(obj + ".rotate.rotateX") + cmds.getAttr(obj + ".jointOrientX")
    tempRY = cmds.getAttr(obj + ".rotate.rotateY") + cmds.getAttr(obj + ".jointOrientY")
    tempRZ = cmds.getAttr(obj + ".rotate.rotateZ") + cmds.getAttr(obj + ".jointOrientZ")

    cmds.setAttr(obj + ".rotate.rotateX", 0)
    cmds.setAttr(obj + ".rotate.rotateY", 0)
    cmds.setAttr(obj + ".rotate.rotateZ", 0)

    cmds.setAttr(obj + ".jointOrientX", tempRX)
    cmds.setAttr(obj + ".jointOrientY", tempRY)
    cmds.setAttr(obj + ".jointOrientZ", tempRZ)

def get_hierarchy_dict(joints):
    """
    Get the hierarchy of joints in a dictionary format.
    """
    hierarchy = {}
    for joint in joints:
        parent = cmds.listRelatives(joint, parent=True)
        hierarchy[joint] = parent[0] if parent else None
    return hierarchy

def IkFkToBind(FKJnt,IKJnt,BindJnt):
    check_and_clear_jointOrient(BindJnt)
    # create choice node
    name_obj = Name_Class.Name(fullname=BindJnt)
    name_obj.type = "choiceNode"
    name_obj.functionType = "IKFKSwitch"
    choice_node = cmds.createNode("choice",name = name_obj.fullname)
    # connect FK and Ik joints to choice node
    cmds.connectAttr(FKJnt + ".worldMatrix[0]", choice_node + ".input[0]")
    cmds.connectAttr(IKJnt + ".worldMatrix[0]", choice_node + ".input[1]")

    # create multmatrix node
    name_obj.type ="multMNode"
    mult_node = cmds.createNode("multMatrix", name=name_obj.fullname)
    cmds.connectAttr(choice_node + ".output", mult_node + ".matrixIn[0]")
    cmds.connectAttr(BindJnt + ".parentInverseMatrix[0]", mult_node + ".matrixIn[1]")

    # create decomposeMatrix node
    name_obj.type = "decompMNode"
    decomp_node = cmds.createNode("decomposeMatrix",name = name_obj.fullname)

    # connect attribute
    # input
    cmds.connectAttr(mult_node + ".matrixSum", decomp_node + ".inputMatrix")
    # output
    cmds.connectAttr(decomp_node + ".outputTranslate", BindJnt + ".translate")
    cmds.connectAttr(decomp_node + ".outputRotate", BindJnt + ".rotate")

    return [choice_node,mult_node,decomp_node]





