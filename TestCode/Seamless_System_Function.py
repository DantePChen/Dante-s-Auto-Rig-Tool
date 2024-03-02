import maya.cmds as cmds
import Switch_Template_Lib as STL
import Name_Class


def createOrEditSwitchTrigger(SeamlessList,switch_ctrl):

    replace_dict = {
        "scriptNode" :SeamlessList[1],
        "triggerFunc" :SeamlessList[0],
        "switch_ctrl" : switch_ctrl
    }
    script_content = STL.CreateSwitchTrigger.format(**replace_dict)
    script_node = cmds.scriptNode(scriptType =2,beforeScript =script_content,name = "switchTrigger")
    cmds.setAttr(script_node + ".sourceType", 1)
    returnlist = [script_content,script_node]
    return returnlist

def createArmScriptNode(switch_ctrl,FKList,IKlist,Bindjnts,infoLoc):
    name_obj = Name_Class.Name(fullname=FKList[0])
    name_obj.description = "Arm"
    name_obj.functionType = "IKFKSwitch"
    name_obj.type = "triggerFunc"
    returnlist = []
    returnlist.append(name_obj.fullname)
    # create a dict for later replacement
    replace_dict = {
        "switch_ctrl": switch_ctrl,
        "FK_Ctrl" : FKList[2],
        "IK_Ctrl" : IKlist[0],
        "PoleVector_Ctrl" : IKlist[1],
        "LocPoleVector" : infoLoc[0],
        "jntArm" : Bindjnts[0],
        "jntElbow": Bindjnts[1],
        "jntWrist": Bindjnts[2],
        "ctrlArm": FKList[0],
        "ctrlElbow": FKList[1],
        "ctrlWrist": FKList[2],
        "triggerFunction":name_obj.fullname
    }

    name_obj.type = "scriptNode"

    script_content = STL.ArmSeamlessSwitch.format(**replace_dict)

    script_node = cmds.scriptNode(scriptType =0,beforeScript =script_content,name = name_obj.fullname)
    cmds.setAttr(script_node + ".sourceType",1)
    returnlist.append(script_node)
    return returnlist