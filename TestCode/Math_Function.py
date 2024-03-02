import maya.cmds as cmds
import maya.OpenMaya as om

def getUnitVector(Mvector):
    magnitude = (Mvector(0)**2+Mvector(1)**2+Mvector(2)**2)**0.5
    unitVec = om.MVector (Mvector(0)/magnitude,Mvector(1)/magnitude,Mvector(2)/magnitude)

    return unitVec

def distance(obj1,obj2):
    p1 = cmds.xform(obj1,query=True, worldSpace=True, translation=True)
    p2 = cmds.xform(obj2,query=True, worldSpace=True, translation=True)

    distance = ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)**0.5
    return distance
