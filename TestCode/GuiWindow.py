from PySide2.QtWidgets import *
import Rig_System_Function as RSF
import Joint_Function as JF
import maya.cmds as cmds
import Assistant_Function as AssF



# define a funtion use for create layout and widget
def q_add(layout,*elements):
    for element in elements:
        if isinstance(element,QLayout):
            layout.addLayout(element)
        elif isinstance(element,QWidget):
            layout.addWidget(element)
    return layout

def q_button(text,action):
    button = QPushButton(text)
    button.clicked.connect(action)
    return button

class CreateWindowTools(QDialog):
    def __init__(self,parent):
        QDialog.__init__(self,parent)
        self.setWindowTitle("Dante's Auto Rig Tool")
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        self.IKCheck = QCheckBox()
        self.FKCheck = QCheckBox()
        self.SwitchCheck = QCheckBox()
        self.BindCheck1 = QCheckBox()
        self.IKCheck1 = QCheckBox()
        self.FKCheck1 = QCheckBox()
        self.SwitchCheck1 = QCheckBox()
        self.BPJnts = []
        self.BindJnts = []
        self.IKReturnList = []
        self.FKReturnList = []
        self.switchList=[]

        q_add(self.layout(),
              q_button("Generate Blueprint Joints", self.GenerateBPJnts),
              q_button("Generate Bind Joints",self.GenerateBindJnts),
              q_add(QHBoxLayout(),
                    q_add(QHBoxLayout(), QLabel(u"IK"), self.IKCheck),
                    q_add(QHBoxLayout(), QLabel(u"FK"), self.FKCheck),
                    q_add(QHBoxLayout(), QLabel(u"Switch"), self.SwitchCheck)
                    ),
              q_button("Generate Rig System",self.GenerateRigSystem),
              q_add(QHBoxLayout(),
                    q_add(QHBoxLayout(), QLabel(u"Bind"), self.BindCheck1),
                    q_add(QHBoxLayout(), QLabel(u"IK"), self.IKCheck1),
                    q_add(QHBoxLayout(), QLabel(u"FK"), self.FKCheck1),
                    q_add(QHBoxLayout(), QLabel(u"Switch"), self.SwitchCheck1)
                    ),
              q_button("Delete and reset",self.DeleteAndReset),
              q_button("snap",self.Snap)
              )

    def GenerateBPJnts(self):
        self.BPJnts = JF.createBaseArmBpjnt()
        print("Blueprint joints generated")

    def GenerateBindJnts(self):
        if not self.BindJnts:
            # first according to the bpjnts to copy a bind joints
            self.BindJnts = RSF.CreateJointChains(self.BPJnts[:-1],"Bind")
            # unparent finger joints for setting up the arm
            fingerlist = [self.BindJnts[3],self.BindJnts[7],self.BindJnts[12],self.BindJnts[17],self.BindJnts[22]]
            for joint in fingerlist:
                cmds.parent(joint,world=True)
                # align the finger separately
                cmds.joint(joint, edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True,
                           zeroScaleOrient=True)
            # calculate the IK plane
            JF.AlignToIKPlane(self.BindJnts[:3])
            # reconstruct the hierarchy
            for joint in fingerlist:
                cmds.parent(joint,self.BindJnts[2])
            print("Bind joints generated")

    def GenerateRigSystem(self):
        # only if switch is not selected, just create IK system
        if self.IKCheck.isChecked() and not self.SwitchCheck.isChecked():
            # if IKReturnList not exist, create Ik system
            if not self.BindJnts:
                cmds.warning("Please generate Bind Joints first")
            else:
                if not self.IKReturnList:
                    self.IKReturnList = RSF.CreateIKArm(self.BindJnts,self.BPJnts)
                    print("IK system generated")

        if self.FKCheck.isChecked() and not self.SwitchCheck.isChecked():
            if not self.BindJnts:
                cmds.warning("Please generate Bind Joints first")
            else:
                if not self.FKReturnList:
                    self.FKReturnList = RSF.CreateFkArm(self.BindJnts)
                    print("FK system generated")

        if self.SwitchCheck.isChecked():
            if not self.BindJnts:
                cmds.warning("Please generate Bind Joints first")
            else:
                if not self.switchList:
                    if not self.IKReturnList:
                        print("no IK sys, creating")
                        self.IKReturnList = RSF.CreateIKArm(self.BindJnts,self.BPJnts)
                    if not self.FKReturnList:
                        print("no FK sys, creating")
                        self.FKReturnList = RSF.CreateFkArm(self.BindJnts)

                    self.switchList = RSF.createSwitchArm(self.BindJnts, self.FKReturnList, self.IKReturnList,self.BPJnts)
                    triggerCode = self.switchList[7]
                    exec(triggerCode)
                    print("Switch system generated")

    def DeleteAndReset(self):
        def deleteBind():
            cmds.delete(self.BindJnts[0])
            self.BindJnts = []
            print("Bind joints has been deleted")

        def deleteIK():
            IK_Ctrl_List = self.IKReturnList[1]
            for obj in IK_Ctrl_List:
                parent = cmds.listRelatives(obj, p=True)
                cmds.delete(parent)
            self.IKReturnList.remove(self.IKReturnList[1])
            for obj in self.IKReturnList:
                cmds.delete(obj)
            self.IKReturnList = []
            print("IK System has been deleted")

        def deleteFK():
            DeleteList = [self.FKReturnList[0][0], self.FKReturnList[1][0]]
            for obj in DeleteList:
                parent = cmds.listRelatives(obj, p=True)
                cmds.delete(parent)
            self.FKReturnList = []
            print("FK System has been deleted")

        # delete Bind
        if self.BindCheck1.isChecked():
            if  self.BindJnts:
                deleteBind()
            else:
                pass
        # delete IK system
        if self.IKCheck1.isChecked():
            if  self.IKReturnList:
                deleteIK()
            else:
                pass

        if self.FKCheck1.isChecked():
            if  self.FKReturnList:
                deleteFK()
            else:
                pass

        if self.SwitchCheck1.isChecked():
            if self.switchList:
                deleteBind()
                deleteIK()
                deleteFK()
                deletlist = [self.switchList[4],self.switchList[6],self.switchList[3][0],self.switchList[3][1]]
                for obj in deletlist:
                    cmds.delete(obj)
                self.switchList=[]
                print("Switch system has been deleted")
            else:
                pass
    def Snap(self):
        AssF.snap_to_pivot()




# Function to get the top-level application window
def get_Top():
    top = QApplication.activeWindow()
    print(top)
    if top is None:
        return
    while True:
        parent = top.parent()
        if parent is None:
            return top
        top = parent

# Function to show the dialog window
def show():
    global window
    if window is None:
        # Create a new QDialog window with the top-level application window as its parent
        window = CreateWindowTools(parent=get_Top())
    # Show the dialog window
    window.show()

if __name__ == "__main__" :
    my_app = QApplication([])
    show()
    my_app.exec_()

window = None
