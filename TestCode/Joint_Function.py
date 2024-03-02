import maya.cmds as cmds
import Name_Class
import Common_Functions as CF
import Attributes_Functions as AF
import maya.OpenMaya as om
import Math_Function as MF


def createFingerJnt(joint_name,num,interval):
    joint_list=[]
    jnt_name=Name_Class.Name(fullname=joint_name)
    i=1
    for i in range(1,num+1):
        jnt_name.index=i
        tempJnt=cmds.joint(name=jnt_name.fullname)
        joint_list.append(tempJnt)
        if i>0:
            cmds.setAttr(tempJnt+".translateX",interval)

    return joint_list


def AlignToIKPlane(IKjoint_list):
    # ungroup these joints
    if cmds.listRelatives(IKjoint_list[1],parent=True):
        cmds.parent(IKjoint_list[1],world = True)
    if cmds.listRelatives(IKjoint_list[2],parent = True):
        cmds.parent(IKjoint_list[2],world = True)
    # reset these joints
    for jnt in IKjoint_list:
        CF.check_and_clear_jointOrient(jnt)

    # create a temp set up for joint3 to aim to
    tempAimCons = cmds.aimConstraint(IKjoint_list[1], IKjoint_list[2], aimVector=[1, 0, 0], offset=(0, 0, 0),
                                 weight=1,
                                 upVector=[0, 1, 0],
                                 worldUpType="scene",
                                 )
    cmds.delete(tempAimCons)
    temploc = cmds.spaceLocator(name="temploc")

    cmds.matchTransform(temploc[0],IKjoint_list[2],position=True,rotation=True,scale=True)
    tempgrp = CF.create_empty_group_and_match_transform(temploc[0])
    cmds.setAttr(temploc[0]+".translateX",-5)
    IKjoint_list.append(temploc[0])
    # get their world position
    jnt0WP=cmds.xform(IKjoint_list[0],query=True, worldSpace=True, translation=True)
    jnt1WP=cmds.xform(IKjoint_list[1],query=True, worldSpace=True, translation=True)
    jnt2WP=cmds.xform(IKjoint_list[2],query=True, worldSpace=True, translation=True)
    jntWP = [jnt0WP,jnt1WP,jnt2WP]

    for i in range(3):
        templist = jntWP.copy()
        templist.remove(jntWP[i])
        # calculate the vector
        V0 = om.MVector(jntWP[i][0] - templist[0][0], jntWP[i][1] - templist[0][1], jntWP[i][2] - templist[0][2])
        v0 = [V0(0),V0(1),V0(2)]
        unitV0 = MF.getUnitVector(V0)

        V1 = om.MVector(jntWP[i][0] - templist[1][0], jntWP[i][1] - templist[1][1], jntWP[i][2] - templist[1][2])
        v1 = [V1(0), V1(1), V1(2)]
        unitV1 = MF.getUnitVector(V1)

        # calculate the perpendicular vector of IK plane
        perpendicular_vec = unitV0^unitV1
        if perpendicular_vec(1)<0:
            perpendicular_vec = om.MVector(-perpendicular_vec(0),-perpendicular_vec(1),-perpendicular_vec(2))
        # move to the joint position
        yup_value = [jntWP[i][0] + perpendicular_vec(0), jntWP[i][1] + perpendicular_vec(1), jntWP[i][2] + perpendicular_vec(2)]
        # create a loc in the position for yup
        yup_loc = cmds.spaceLocator(name = "yup_loc")
        AF.SetTransform(yup_loc[0],Translation=yup_value,Rotation=[0,0,0],Scale=[1,1,1])
        # create a aimConstraint for joint to fix the axis
        aimCons = cmds.aimConstraint(IKjoint_list[i+1],IKjoint_list[i],aimVector = [1,0,0], offset=(0, 0, 0),
        weight=1,
        upVector=[0, 1, 0],
        worldUpType="object",
        worldUpObject=yup_loc[0])
        # delete the temp constraint and yup_loc
        cmds.delete(aimCons)
        cmds.delete(yup_loc)
        # bake rotation
        CF.bake_Rotation(IKjoint_list[i])
    # delete the temp obj
    cmds.delete(temploc)
    cmds.delete(tempgrp)
    # reset the hierarchy
    cmds.parent(IKjoint_list[2],IKjoint_list[1])
    cmds.parent(IKjoint_list[1],IKjoint_list[0])









def createBaseArmBpjnt():
    bpjnt_list=[]
    #shoulder bpjnt
    bpjntShoulderName=Name_Class.Name(fullname="bpjnt_R_Shoulder_001")
    bpjntShoulder = cmds.createNode("joint",name=bpjntShoulderName.fullname)
    cmds.setAttr(bpjntShoulder + ".translateX", -20)
    cmds.setAttr(bpjntShoulder + ".translateY", 147)
    cmds.setAttr(bpjntShoulder + ".translateZ", -6)
    cmds.setAttr(bpjntShoulder + ".rotateY", -180)
    bpjnt_list.append(bpjntShoulder)

    #elbow bpjnt
    bpjntElbowName = Name_Class.Name(fullname="bpjnt_R_Elbow_001")
    bpjntElbow = cmds.createNode("joint", name=bpjntElbowName.fullname)
    cmds.setAttr(bpjntElbow + ".translateX", -45)
    cmds.setAttr(bpjntElbow + ".translateY", 147)
    cmds.setAttr(bpjntElbow + ".translateZ", -6.5)
    cmds.setAttr(bpjntElbow + ".rotateY", -180)
    bpjnt_list.append(bpjntElbow)

    #wrist bpjnt
    bpjntWristName = Name_Class.Name(fullname="bpjnt_R_Wrist_001")
    bpjntWrist = cmds.createNode("joint", name=bpjntWristName.fullname)
    cmds.setAttr(bpjntWrist + ".translateX", -73)
    cmds.setAttr(bpjntWrist + ".translateY", 147)
    cmds.setAttr(bpjntWrist + ".translateZ", -6)
    cmds.setAttr(bpjntWrist + ".rotateY", -180)
    bpjnt_list.append(bpjntWrist)

    #polevector bploc
    locPoleVectorName = Name_Class.Name(fullname="loc_R_ArmPoleVector_001")
    locArmPV= cmds.spaceLocator(name=locPoleVectorName.fullname)
    CF.MTP(bpjntElbow,locArmPV)

    # finger Bpjnts
    cmds.select(bpjntWrist)
    Thumb_Joints=createFingerJnt(joint_name="bpjnt_R_Thumb_001",num=4,interval=2)
    bpjnt_list+=Thumb_Joints
    AF.SetTransform(obj=Thumb_Joints[0],Translation=[2,0,-4.5],Rotation=[0,60,0],Scale=[1,1,1])
    cmds.select(bpjntWrist)
    Index_Joints=createFingerJnt(joint_name="bpjnt_R_Index_001",num=5,interval=2.5)
    AF.SetTransform(obj=Index_Joints[0],Translation=[7,0,-4],Rotation=[0,0,0],Scale=[1,1,1])
    bpjnt_list+=Index_Joints
    cmds.select(bpjntWrist)
    Middle_Joints=createFingerJnt(joint_name="bpjnt_R_Middle_001",num=5,interval=2.8)
    AF.SetTransform(obj=Middle_Joints[0],Translation=[7.5,0,-1.5],Rotation=[0,0,0],Scale=[1,1,1])
    bpjnt_list+=Middle_Joints
    cmds.select(bpjntWrist)
    Ring_Joints=createFingerJnt(joint_name="bpjnt_R_Ring_001",num=5,interval=2.2)
    AF.SetTransform(obj=Ring_Joints[0],Translation=[6.8,0,1],Rotation=[0,0,0],Scale=[1,1,1])
    bpjnt_list+=Ring_Joints
    cmds.select(bpjntWrist)
    Pinky_Joints=createFingerJnt(joint_name="bpjnt_R_Pinky_001",num=5,interval=2)
    AF.SetTransform(obj=Pinky_Joints[0],Translation=[6.5,0,3.5],Rotation=[0,0,0],Scale=[1,1,1])
    bpjnt_list+=Pinky_Joints

    bpjnt_list+=locArmPV
    cmds.parent(bpjntElbow,bpjntShoulder)
    cmds.parent(bpjntWrist,bpjntElbow)
    cmds.parent(locArmPV,bpjntElbow)
    AF.SetTransform(obj=locArmPV[0], Translation=[0, 0, 30], Rotation=[0, 0, 0], Scale=[1, 1, 1])

    return bpjnt_list



def createTwistJoints(joint_list, i):
    # Check if the joint_list has at least 2 joints to create twists
    if len(joint_list) < 2:
        raise ValueError("Joint list should have at least 2 joints for creating twists.")

    new_joints = []

    # Iterate through the joints list to create twists
    for j in range(len(joint_list) - 1):  # For each pair of joints in the list
        joint0 = joint_list[j]
        joint1 = joint_list[j + 1]

        # Get positions of the joints
        pos0 = cmds.xform(joint0, query=True, worldSpace=True, translation=True)
        pos1 = cmds.xform(joint1, query=True, worldSpace=True, translation=True)

        # Calculate distances between joints
        dist01 = [(pos1[axis] - pos0[axis]) for axis in range(3)]

        # Create joints between joint0 and joint1
        for step in range(1, i + 1):
            newPos0 = [
                pos0[axis] + dist01[axis] * step / (i + 1) for axis in range(3)
            ]
            newName = Name_Class.Name(fullname=joint0)
            newName.functionType = "Twist"
            newName.index = step
            newJoint0 = cmds.joint(name=newName.fullname)
            cmds.xform(newJoint0, translation=newPos0, worldSpace=True)
            new_joints.append(newJoint0)

        # Set hierarchy
        if j == 0:
            cmds.parent(new_joints[0], joint0)
            cmds.parent(joint1, new_joints[i - 1])
        if j>0:
            print(joint1)
            print(new_joints[i-1])
            cmds.parent(joint1, new_joints[i - 1])

        new_joints.clear()






