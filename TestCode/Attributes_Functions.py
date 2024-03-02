import maya.cmds as cmds

def hide_attributes(target_object, *args):
    # if no arg was chosen, hide all the attributes
    attrs_list = ["translateX", "translateY", "translateZ",
                         "rotateX", "rotateY", "rotateZ",
                         "scaleX", "scaleY", "scaleZ", "visibility"]
    for attr in attrs_list:
        cmds.setAttr(target_object + "." + attr, lock=False, keyable=False)
    # then show the args were chosen
    for attr in args:
        cmds.setAttr(target_object + "." + attr, lock=False, keyable=True)


def add_attribute(target_object, attr_name, dataType, **kwargs):
    attr_args = {"ln": attr_name, "attributeType": dataType}
    attr_args.update(kwargs)

    if dataType in ["float", "double"]:
        if "setMin" in attr_args:
            attr_args["minValue"] = attr_args.pop("setMin")
        else:
            attr_args.setdefault("minValue", 0)

        if "setMax" in attr_args:
            attr_args["maxValue"] = attr_args.pop("setMax")
        else:
            attr_args.setdefault("maxValue", 1)

        if "setDefault" in attr_args:
            attr_args["defaultValue"] = attr_args.pop("setDefault")
        else:
            attr_args.setdefault("defaultValue", 0)

    elif dataType == "enum":
        enum_values = attr_args.pop("enum_values", [])
        attr_args.setdefault("enumName", ":".join(enum_values))

    cmds.addAttr(target_object, **attr_args)
    if not attr_args.get("keyable", True):
        cmds.setAttr(target_object + "." + attr_name, cb=True)

def SetTransform(obj,Translation, Rotation, Scale):
    cmds.setAttr(obj + ".translateX", Translation[0])
    cmds.setAttr(obj + ".translateY", Translation[1])
    cmds.setAttr(obj + ".translateZ", Translation[2])

    cmds.setAttr(obj + ".rotateX", Rotation[0])
    cmds.setAttr(obj + ".rotateY", Rotation[1])
    cmds.setAttr(obj + ".rotateZ", Rotation[2])

    cmds.setAttr(obj + ".scaleX", Scale[0])
    cmds.setAttr(obj + ".scaleY", Scale[1])
    cmds.setAttr(obj + ".scaleZ", Scale[2])