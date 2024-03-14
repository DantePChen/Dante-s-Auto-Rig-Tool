import maya.cmds as cmds
import Name_Class
import Common_Functions as CMF
import Ctrl_Functions as CF
import Attributes_Functions as AF
import Seamless_System_Function as SSF
import Math_Function as MF


def CreateJointChains(input_joints,functionType):
    joints_list=[]
    # create a dic to store the hierarchy of input_joints
    joint_hierarchy_dic = CMF.get_hierarchy_dict(input_joints)
    # copy a new dic to store the new hierarchy
    new_dic = dict(joint_hierarchy_dic)
    for input_joint in input_joints:
        name_obj = Name_Class.Name(fullname=input_joint)
        name_obj.type = "jnt"
        name_obj.functionType = functionType
        newJnt = cmds.createNode("joint", name=name_obj.fullname)
        # Update the dictionary if input_joint is a key
        if input_joint in new_dic:
            new_dic[newJnt] = new_dic.pop(input_joint)

        # Update the dictionary if input_joint is a value
        for key, val in new_dic.items():
            if val == input_joint:
                new_dic[key] = newJnt

        CMF.MTP(input_joint, newJnt)
        CMF.bake_Rotation(newJnt)

        joints_list.append(newJnt)
    for newJnt in joints_list:
        parent_joint = new_dic[newJnt]
        if parent_joint:
            cmds.parent(newJnt,parent_joint)
    return  joints_list


def CreateFkArm(blueprint_joints):
    # from blueprint_joints create fk joints
    FK_joints=CreateJointChains(input_joints=blueprint_joints,functionType="FK")
    cmds.select(clear=True)
    name_obj = Name_Class.Name(fullname=FK_joints[0])
    name_obj.type="sys"
    name_obj.description="Arm"
    FKJointGP = cmds.group(em=True,n=name_obj.fullname)
    cmds.parent(FK_joints[0],FKJointGP)

    # prepare a list to store the controllers
    circle_controllers = []
    joint_hierarchy =CMF.get_hierarchy_dict(FK_joints)

    # set the first joints
    CMF.create_Fk_ctrl(FK_joints[0], ctrlType="Main_Fk_Ctrl", degree=1, size=0, color="blue", controller_lists=circle_controllers)
    # set zero group for first ctrl
    CMF.MTP(FK_joints[0], circle_controllers[0])
    CMF.create_empty_group_and_match_transform(circle_controllers[0])
    CMF.check_and_clear_jointOrient(FK_joints[0])
    CMF.Matrix_Paren_Constrain(circle_controllers[0], FK_joints[0])
    i = 0
    for object in FK_joints[1:]:
        # first check if it's zero, if yes, make ctrls
        if CMF.check_if_Zero(object) == 1:
            #use dic to get the right hierarchy
            parent =joint_hierarchy[object]
            # create the fk control
            if i<=1:
                CMF.create_Fk_ctrl(object, ctrlType="Normal_Fk_Ctrl", degree=1, size=0, color="blue",
                                   controller_lists=circle_controllers)
            if i>1:
                CMF.create_Fk_ctrl(object, ctrlType="ring", degree=0, size=2, color="blue", controller_lists=circle_controllers)
            # get the fk control
            circle_ctrl = circle_controllers[-1]
            circle_ctrl_parent = None if not parent else circle_controllers[FK_joints.index(parent)]
            # match joint and ctrl
            CMF.MTP(object, circle_ctrl)
            cmds.parent(circle_ctrl, circle_ctrl_parent)
            i+=1
        else:
            raise RuntimeError("The rotation of " + object + " is not zero. Stopping running")


    # make connections
    for ctrl, joint in zip(circle_controllers[1:], FK_joints[1:]):
        CMF.create_empty_group_and_match_transform(ctrl)
        CMF.connect_RotateAttr(ctrl, joint)

    # delete the tip ctrl
    for ctrl in [circle_controllers[6],circle_controllers[10],circle_controllers[14],circle_controllers[18],circle_controllers[22]]:
        parent = cmds.listRelatives(ctrl,parent=True)
        cmds.delete(parent)

    # set attributes
    Three_Rotation_List = [circle_controllers[0],circle_controllers[2],circle_controllers[7],circle_controllers[11],circle_controllers[15],circle_controllers[19]]
    Three_Rotation_List += circle_controllers[3:5]
    for ctrl in Three_Rotation_List:
        AF.hide_attributes(ctrl,"rotateX", "rotateY", "rotateZ")

    RotationZ_List = circle_controllers[8:10]+circle_controllers[12:14]+circle_controllers[16:18]+circle_controllers[20:22]
    RotationZ_List.append(circle_controllers[1])
    RotationZ_List.append(circle_controllers[5])
    for ctrl in RotationZ_List:
        AF.hide_attributes(ctrl,"rotateZ")

    # prepare the return list

    FK_joints_list = FK_joints
    FK_ctrl_list = circle_controllers[:3]
    fingerStart_List = [circle_controllers[3],circle_controllers[7],circle_controllers[11],circle_controllers[15],circle_controllers[19]]
    return_list=[FK_joints_list,FK_ctrl_list,fingerStart_List,FKJointGP]

    return return_list



def CreateIKArm(Bind_joints,blueprint_joints):
    temp_name = Name_Class.Name(Bind_joints[0])
    # base on the input joints, create Ik joints chain
    IK_Joints=CreateJointChains(input_joints=Bind_joints[:3], functionType="IK")
    cmds.select(clear=True)
    name_obj = Name_Class.Name(fullname=IK_Joints[0])
    name_obj.type = "sys"
    name_obj.description = "Arm"
    IKJointGP = cmds.group(em=True, n=name_obj.fullname)
    cmds.parent(IK_Joints[0], IKJointGP)
    IKConnectGP = CMF.create_empty_group_and_match_transform(IK_Joints[0])
    name_obj.type = "connect"
    IKConnectGP = cmds.rename(IKConnectGP,name_obj.fullname)

    # create IK hand
    ArmIKHandle = cmds.ikHandle(startJoint=IK_Joints[0],endEffector=IK_Joints[2])
    # create IK ctrl
    temp_name.type = "ctrl"
    temp_name.description = "Arm"
    temp_name.functionType = "IK"
    IK_Ctrl=CF.createCtrl(ctrlName=temp_name.fullname,ctrlType="Cube_Ctrl",degree=1,size=0,color="blue")
    # set up for IK ctrl
    CMF.MTP(IK_Joints[2], IK_Ctrl)
    CMF.bake_Rotation(IK_Ctrl)
    cmds.parent(ArmIKHandle[0], IK_Ctrl)
    cmds.setAttr(ArmIKHandle[0]+".visibility",0)
    CMF.Matrix_Rotation_Constrain(parent=IK_Ctrl,child=IK_Joints[2])
    empty_group = cmds.group(em=True, name=IK_Ctrl.replace("ctrl_", "Zero_"))
    cmds.matchTransform(empty_group,IK_Ctrl,pos=True,rot=False,scl=True)
    cmds.parent(IK_Ctrl,empty_group)

    #set up for polevector ctrl
    temp_name.description = "ArmPoleVector"
    PV_Ctrl = CF.createCtrl(ctrlName=temp_name.fullname,ctrlType="PoleVector_Ctrl",degree=1,size=0,color="blue")
    distance = MF.distance(blueprint_joints[-1],Bind_joints[1])
    cmds.matchTransform(PV_Ctrl, Bind_joints[1], pos=True, rot=False, scl=True)
    cmds.parent(PV_Ctrl,Bind_joints[1])
    cmds.setAttr(PV_Ctrl + ".translateY",distance)
    cmds.parent(PV_Ctrl,world=True)
    CMF.create_empty_group_and_match_transform(PV_Ctrl)
    cmds.poleVectorConstraint(PV_Ctrl,ArmIKHandle[0])

    # set up for guideline
    temp_name.type = "guideline"
    temp_name.description = "Arm"
    guide_line = CF.createGuideline(name=temp_name.fullname,joint=IK_Joints[1],PoleVector=PV_Ctrl)

    # set up IK root
    temp_name.type = "IKRoot"
    IK_Root = cmds.spaceLocator(name = temp_name.fullname)
    CMF.MTP(parent=Bind_joints[0],child=IK_Root[0])
    CMF.Matrix_Paren_Constrain(parent=IK_Root[0],child=IKConnectGP)

    #set attributes
    AF.hide_attributes(PV_Ctrl,"translateX","translateY","translateZ")
    AF.hide_attributes(IK_Ctrl,"translateX","translateY","translateZ","rotateX", "rotateY", "rotateZ")

    #prepare return list
    IK_joints_list = IK_Joints[:3]
    IK_ctrl_list = [IK_Ctrl,PV_Ctrl]
    return_list = [IK_joints_list,IK_ctrl_list,IKJointGP,IK_Root,guide_line]

    return return_list

def createSwitchArm(Bindjnts,FKReturnList,IKReturnList,BpJnt):
    # get the required obj from list
    FK_Joints = FKReturnList[0]
    FK_Ctrls =FKReturnList[1]
    IK_Joints = IKReturnList[0]
    IK_Ctrls = IKReturnList[1]
    guide_line = IKReturnList[4]
    fingerStart_List = FKReturnList[2]
    IKJointGP = IKReturnList[2]
    FKJointGP = FKReturnList[3]


    # build connection between FK,IK,Bind joints
    choice_list=[]
    multinode_list=[]
    decomp_list = []
    for FKJnt, IKJnt, BindJnt in zip(FK_Joints[:3], IK_Joints, Bindjnts[:3]):
        nodelist = CMF.IkFkToBind(FKJnt=FKJnt,IKJnt=IKJnt,BindJnt=BindJnt)
        choice_node = nodelist[0]
        multi_node = nodelist[1]
        decomp_node = nodelist[2]
        choice_list.append(choice_node)
        multinode_list.append(multi_node)
        decomp_list.append(decomp_node)


    # create switch ctrl
    name_obj = Name_Class.Name(fullname=FK_Ctrls[0])
    name_obj.description = "Arm"
    name_obj.functionType = "IKFKSwitch"
    switch_ctrl = CF.createCtrl(ctrlName=name_obj.fullname,ctrlType="Switch_Ctrl",degree=1,size=0,color="blue")
    AF.SetTransform(obj=switch_ctrl,Translation = [-20,160,-6],Rotation=[0,0,0],Scale=[1,1,1])
    AF.hide_attributes(target_object=switch_ctrl)
    AF.add_attribute(target_object=switch_ctrl,attr_name="IKFKSwitch",dataType="enum",keyable = True,enum_values =["FK","IK"])

    # set switch function
    for choice_node in choice_list:
        cmds.connectAttr(switch_ctrl + ".IKFKSwitch",choice_node + ".selector")

    name_obj.type = "ReverseNode"
    reverse_node = cmds.createNode("reverse",name = name_obj.fullname)
    cmds.connectAttr(switch_ctrl + ".IKFKSwitch", reverse_node + ".inputX")
    for FK_Ctrl in FK_Ctrls:
        cmds.connectAttr(reverse_node + ".outputX", FK_Ctrl + ".visibility")
    for IK_Ctrl in IK_Ctrls:
        cmds.connectAttr(switch_ctrl + ".IKFKSwitch", IK_Ctrl + ".visibility")
    cmds.connectAttr(switch_ctrl + ".IKFKSwitch", guide_line + ".visibility")

    # set for hand ctrls
    name_obj.type = "space"
    name_obj.description = "hand"
    name_obj.functionType = "None"
    hand_grp = cmds.group(em=True,name = name_obj.fullname)
    CMF.Matrix_Paren_Constrain(parent=Bindjnts[2],child=hand_grp)
    for finger_ctrl in fingerStart_List:
        tempParent = cmds.listRelatives(finger_ctrl,parent = True)
        cmds.parent(tempParent,hand_grp)
    for FKJnt, BindJnt in zip(FK_Joints[3:],  Bindjnts[3:]):
        CMF.connect_RotateAttr(FKJnt, BindJnt)

    # set seamless switch function
    name_obj = Name_Class.Name(fullname=FK_Ctrls[0])
    name_obj.type = "infoLoc"
    name_obj.description = "PoleVector"
    name_obj.functionType = "IK"
    infoLoc = cmds.spaceLocator(name = name_obj.fullname)
    CMF.MTP(parent=IK_Ctrls[1],child=infoLoc)
    cmds.parent(infoLoc,FK_Joints[0])

    # create seamless switch attribute
    AF.add_attribute(target_object=switch_ctrl, attr_name="SeamlessSwitch", dataType="enum", keyable=False,
                     enum_values=["FK", "IK"])

    # set visibility to some object
    cmds.setAttr(BpJnt[0]+".visibility", 0 )
    cmds.setAttr(IKJointGP+".visibility",0 )
    cmds.setAttr(FKJointGP+".visibility",0 )

    # create scriptNode for seamless switch
    SeamlessList = SSF.createArmScriptNode(switch_ctrl,FK_Ctrls,IK_Ctrls,Bindjnts,infoLoc)
    triggerlist = SSF.createOrEditSwitchTrigger(SeamlessList,switch_ctrl)
    Trigger_code = triggerlist[0]
    scriptNode_list = [SeamlessList[1],triggerlist[1]]

    returnlist = [choice_list, multinode_list, decomp_list, scriptNode_list, switch_ctrl, reverse_node, hand_grp,
                  Trigger_code]
    return returnlist
