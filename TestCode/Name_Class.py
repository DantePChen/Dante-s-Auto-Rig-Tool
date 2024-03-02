class Name(object):
    # name convention class
    def __init__(self, fullname=None, type=None, side=None, resolution=None, description=None, functionType=None, index=None):
        self._type = type
        self._side = side
        self._resolution = resolution
        self._description = description
        self._functionType = functionType
        self._index = index

        self._fullname = fullname

        if self._fullname:
            self.decompose()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, value):
        self._side = value

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, value):
        self._resolution = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def functionType(self):
        return self._functionType

    @functionType.setter
    def functionType(self, value):
        self._functionType = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def fullname(self):
        self.compose()
        return self._fullname

    def compose(self):
        self._fullname = ""

        # put together all parts of the name
        parts = [self._type, self._side, self._resolution, self._description, self._functionType ]
        for name_part in parts:
            if name_part == "None":  # if the string is "None"
                parts.remove(name_part)  # then delete this part

        for name_part in parts:
            if name_part:
                self._fullname += "{}_".format(name_part)

        # add index
        self._fullname = "{}{:03d}".format(self._fullname, self._index)

    def decompose(self):
        name_parts = self._fullname.split('_')

        self._type = name_parts[0]
        self._side = name_parts[1]
        resolution_candidates = ["high", "middle", "low"]
        for part in name_parts:
            if part in resolution_candidates:
                self._resolution = part
                break
        else:
            self._resolution = None
        function_candidates =["IK","FK","HyperIKFK","Bind","Twist","IKFKSwitch","SpaceSwitch"]
        for part in name_parts:
            if part in function_candidates:
                self._functionType = part
                self._description = name_parts[-3]
                break
            else:
                self._functionType = None
                self._description = name_parts[-2]
        self._index = int(name_parts[-1])

    def flip(self):
        if self._side == "L":
            self._side = "R"
        elif self._side == "R":
            self._side = "L"

    def next(self):
        self._index+=1