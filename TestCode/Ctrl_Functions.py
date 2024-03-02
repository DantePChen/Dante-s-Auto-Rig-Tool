import maya.cmds as cmds
import Ctrl_Lib as CL
import Name_Class
import Common_Functions as CMF



def createCtrl(ctrlName,ctrlType,degree,size,color):
    #input parameter
    global ctrl_curve
    flag=1
    degree_value= degree
    size_value = size

    color_value = 0
    if "blue" in color.lower():
        color_value = 6
    elif "red" in color.lower():
        color_value = 13
    elif "yellow" in color.lower():
        color_value = 17

    point_list = []
    # if type is ring, just create simple ring ctrls
    if ctrlType=="ring":
        circle_curve = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), r=size_value, name=ctrlName)
        # because of cmds.circle return a list contain both obj and its shape node, need to be separate
        ctrl_curve=circle_curve[0]

    # depends on the type, choose different points list in the lib
    else:
        if ctrlType == "Main_Fk_Ctrl":
            point_list = CL.Main_Fk_Ctrl
        elif ctrlType == "Normal_Fk_Ctrl":
            point_list = CL.Normal_Fk_Ctrl
        elif ctrlType == "Cube_Ctrl":
            point_list = CL.Cube_Ctrl
            flag=0
        elif ctrlType == "PoleVector_Ctrl":
            point_list = CL.PoleVector_Ctrl
        elif ctrlType == "Switch_Ctrl":
            point_list = CL.Switch_Ctrl
        # if flag is 1, the normal setup ways
        if flag==1:
            # create the curve
            ctrl_curve = cmds.curve(name=ctrlName, degree=degree_value, p=point_list)
            # set the color
            cmds.closeCurve(ctrl_curve, ch=False, replaceOriginal=True)
            shap_node = cmds.listRelatives(ctrl_curve,children=True)
            # rename the shape node
            cmds.rename(shap_node,ctrl_curve+"shape")
        # if flag =0, make ik ctrl
        if flag==0:
            # create a temp curve, only the shape node is needed
            tempshape = cmds.curve(name="temp", degree=degree_value, p=point_list)
            # create a joint, which is actually the real controller
            ctrl_curve = cmds.createNode("joint", name=ctrlName)
            # get the shape node of the curve
            shape_node = cmds.listRelatives(tempshape,children=True)
            # put the shape under the joint, and delete original curve
            cmds.parent(shape_node, ctrl_curve, shape=True, add=True)
            cmds.delete(tempshape)
            # make joint invisible
            cmds.setAttr(ctrl_curve + ".radius", 0)
            cmds.setAttr(ctrl_curve + ".radius", cb=False)
            # rename the shape node
            shap_node = cmds.listRelatives(ctrl_curve, children=True)
            cmds.rename(shap_node, ctrl_curve + "shape")



    cmds.setAttr(ctrl_curve + ".overrideEnabled", 1)
    cmds.setAttr(ctrl_curve + ".overrideColor", color_value)

    return ctrl_curve

def createGuideline(name,joint,PoleVector):

    name_obj = Name_Class.Name(fullname=name)

    # create guide_line curve
    guideline = cmds.curve(name=name_obj.fullname, degree=1, p=[(0.0, 0.0, 0.0), (0.0, 0.0, -2.0)])

    # get the shape node
    guideline_shape = cmds.listRelatives(guideline, children= True)

    # create two locator
    name_obj.type ="GLLoc"
    name_obj.index=1
    loc1 = cmds.spaceLocator(name=name_obj.fullname)
    CMF.MTP(parent=joint, child=loc1[0])
    cmds.parent(loc1[0],joint)
    name_obj.index=2
    loc2 = cmds.spaceLocator(name=name_obj.fullname)
    CMF.MTP(parent=PoleVector, child=loc2[0])
    cmds.parent(loc2[0],PoleVector)

    # get the two shape node of two loc
    loc1_shape = cmds.listRelatives(loc1[0], children= True)
    loc2_shape = cmds.listRelatives(loc2[0],children = True)

    # set the guildline
    cmds.connectAttr(loc1_shape[0] + ".worldPosition", guideline_shape[0] + ".controlPoints[0]")
    cmds.connectAttr(loc2_shape[0] + ".worldPosition", guideline_shape[0] + ".controlPoints[1]")

    # set some attributes
    cmds.setAttr(loc1[0] + ".visibility",0)
    cmds.setAttr(loc2[0] + ".visibility",0)
    cmds.setAttr(guideline + ".overrideEnabled", 1)
    cmds.setAttr(guideline + ".overrideDisplayType", 2)

    return guideline
