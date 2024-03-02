ArmSeamlessSwitch = """
import maya.cmds as cmds

switch_ctrl = "{switch_ctrl}"
IKFK_switch_value = cmds.getAttr(switch_ctrl + ".IKFKSwitch")


def MTP(parent, child):
    # create the parentConstrain to match the child and parent
    constraint_name = cmds.parentConstraint(parent, child, maintainOffset=False)
    # delete the constraint node
    cmds.delete(constraint_name)

def FKToIK():
    # set variables for every object
    FKCtrl = "{FK_Ctrl}"
    IKCtrl = "{IK_Ctrl}"
    PV = "{PoleVector_Ctrl}"
    LocPV = "{LocPoleVector}"

    # execute switch function
    MTP(parent=FKCtrl,child=IKCtrl)
    MTP(parent=LocPV,child=PV)
    cmds.setAttr(PV + ".rotateX", 0)
    cmds.setAttr(PV + ".rotateY", 0)
    cmds.setAttr(PV + ".rotateZ", 0)

    #set Switch value
    cmds.setAttr(switch_ctrl + ".IKFKSwitch", 1)


def IKToFK():
    jnt_list = ["{jntArm}","{jntElbow}","{jntWrist}"]
    ctrl_list = ["{ctrlArm}","{ctrlElbow}","{ctrlWrist}"]

    for jnt,ctrl in zip(jnt_list,ctrl_list):
        MTP(parent=jnt,child=ctrl)

    # set Switch value
    cmds.setAttr(switch_ctrl + ".IKFKSwitch", 0)



if IKFK_switch_value == 0:
    FKToIK()
else:
    IKToFK()

# reselect the ctrl
cmds.select(switch_ctrl)


"""

CreateSwitchTrigger ="""
import maya.cmds as cmds
global {triggerFunc}
def {triggerFunc}():
    cmds.scriptNode("{scriptNode}",executeBefore=True)
    print("switch done")
    cmds.scriptJob(runOnce=True, attributeChange=["{switch_ctrl}" + ".SeamlessSwitch", {triggerFunc}])

cmds.scriptJob(runOnce=True, attributeChange=["{switch_ctrl}" + ".SeamlessSwitch", {triggerFunc}])


"""