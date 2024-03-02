import Name_Class
import maya.cmds as cmds

def test(obj_list):
    for obj in obj_list:
        name_obj = Name_Class.Name(fullname=obj)
        print(name_obj.fullname)
        print(name_obj.type)
        print(name_obj.functionType)
