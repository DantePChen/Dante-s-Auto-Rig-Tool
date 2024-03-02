import maya.cmds as cmds


def snap_to_pivot():
    """
    snap the last selected object to other selected nodes' average pivot position
    """
    # get selected nodes, the last one is the one need to be snapped, others are drivers
    selected_nodes = cmds.ls(selection=True, flatten=True)

    if not selected_nodes or len(selected_nodes) < 2:
        cmds.warning('need to select at least two nodes to do the snap')
    else:
        driver_nodes = selected_nodes[:-1]
        driven_node = selected_nodes[-1]

        # get driver nodes' xyz in different lists
        drivers_x = []
        drivers_y = []
        drivers_z = []

        for driver in driver_nodes:
            pos = cmds.xform(driver, query=True, translation=True, worldSpace=True)
            drivers_x.append(pos[0])
            drivers_y.append(pos[1])
            drivers_z.append(pos[2])

        # get maximum and minimum values
        max_x = max(drivers_x)
        min_x = min(drivers_x)

        max_y = max(drivers_y)
        min_y = min(drivers_y)

        max_z = max(drivers_z)
        min_z = min(drivers_z)

        # get center position for xyz
        pos_x = 0.5 * max_x + 0.5 * min_x
        pos_y = 0.5 * max_y + 0.5 * min_y
        pos_z = 0.5 * max_z + 0.5 * min_z

        # set driven node's position
        cmds.xform(driven_node, translation=[pos_x, pos_y, pos_z], worldSpace=True)
