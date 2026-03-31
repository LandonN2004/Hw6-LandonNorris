#region imports
from scipy.optimize import fsolve
from Resistor import Resistor
from VoltageSource import VoltageSource
from Loop import Loop
#endregion

#region class definitions
class ResistorNetwork():
    #region constructor
    def __init__(self):
        """
        The resistor network consists of Loops, Resistors and Voltage Sources.
        This is the constructor for the network and it defines fields for Loops, Resistors and Voltage Sources.
        You can populate these lists manually or read them in from a file.
        """
        #region attributes
        self.Loops = []
        self.Resistors = []
        self.VSources = []
        #endregion
    #endregion

    #region methods
    def BuildNetworkFromFile(self, filename):
        """
        This function reads the lines from a file and processes the file to populate the fields
        for Loops, Resistors and Voltage Sources
        :param filename: string for file to process
        :return: nothing
        """
        FileTxt = open(filename, "r").read().split('\n')
        self.Resistors = []
        self.VSources = []
        self.Loops = []
        LineNum = 0
        FileLength = len(FileTxt)
        while LineNum < FileLength:
            lineTxt = FileTxt[LineNum].lower().strip()
            if len(lineTxt) < 1:
                pass
            elif lineTxt[0] == '#':
                pass
            elif "resistor" in lineTxt:
                LineNum = self.MakeResistor(LineNum, FileTxt)
            elif "source" in lineTxt:
                LineNum = self.MakeVSource(LineNum, FileTxt)
            elif "loop" in lineTxt:
                LineNum = self.MakeLoop(LineNum, FileTxt)
            LineNum += 1

    def MakeResistor(self, N, Txt):
        """
        Make a resistor object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: updated line number
        """
        R = Resistor()
        N += 1
        txt = Txt[N].lower()
        while "</resistor>" not in txt:
            if "name" in txt:
                R.Name = txt.split('=')[1].strip()
            if "resistance" in txt:
                R.Resistance = float(txt.split('=')[1].strip())
            N += 1
            txt = Txt[N].lower()

        self.Resistors.append(R)
        return N

    def MakeVSource(self, N, Txt):
        """
        Make a voltage source object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: updated line number
        """
        VS = VoltageSource()
        N += 1
        txt = Txt[N].lower()
        while "</source>" not in txt:
            if "name" in txt:
                VS.Name = txt.split('=')[1].strip()
            if "value" in txt:
                VS.Voltage = float(txt.split('=')[1].strip())
            if "type" in txt:
                VS.Type = txt.split('=')[1].strip()
            N += 1
            txt = Txt[N].lower()

        self.VSources.append(VS)
        return N

    def MakeLoop(self, N, Txt):
        """
        Make a Loop object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: updated line number
        """
        L = Loop()
        N += 1
        txt = Txt[N].lower()
        while "</loop>" not in txt:
            if "name" in txt:
                L.Name = txt.split('=')[1].strip()
            if "nodes" in txt:
                txt = txt.replace(" ", "")
                L.Nodes = txt.split('=')[1].strip().split(',')
            N += 1
            txt = Txt[N].lower()

        self.Loops.append(L)
        return N

    def AnalyzeCircuit(self):
        """
        Use fsolve to find currents in the original resistor network.
        Unknowns are the currents labeled I1, I2, I3 on the homework figure.
        :return: numpy array of solved currents
        """
        i0 = [1.0, 1.0, 1.0]
        i = fsolve(self.GetKirchoffVals, i0)
        print(f"I1 = {i[0]:0.4f} A")
        print(f"I2 = {i[1]:0.4f} A")
        print(f"I3 = {i[2]:0.4f} A")
        return i

    def GetKirchoffVals(self, i):
        """
        Original circuit equations.
        Current directions match the arrows shown in the homework figure:
        I1: a -> b on the top branch
        I2: d -> e on the bottom-right branch
        I3: c -> d through the 1 ohm resistor
        """
        I1, I2, I3 = i

        # Map figure-current directions onto resistor directions (alphabetical resistor names)
        self.GetResistorByName('ad').Current = -I1  # actual current is d -> a
        self.GetResistorByName('bc').Current = I1   # actual current is b -> c
        self.GetResistorByName('cd').Current = I3   # actual current is c -> d
        self.GetResistorByName('ce').Current = -I2  # actual current is e -> c

        Node_c_Current = I1 + I2 - I3
        KVL = self.GetLoopVoltageDrops()
        KVL.append(Node_c_Current)
        return KVL

    def GetElementDeltaV(self, name):
        """
        Retrieve the signed voltage change for either a resistor or a voltage source.
        Traversing a resistor in the current direction gives a voltage drop (-IR).
        Traversing opposite the current direction gives a voltage rise (+IR).
        Voltage-source sign comes from the ordering of the source name in the text file.
        """
        for r in self.Resistors:
            if name == r.Name:
                return -r.DeltaV()
            if name[::-1] == r.Name:
                return r.DeltaV()
        for v in self.VSources:
            if name == v.Name:
                return v.Voltage
            if name[::-1] == v.Name:
                return -v.Voltage
        raise ValueError(f"No circuit element found with name {name}")

    def GetLoopVoltageDrops(self):
        """
        Calculates the net voltage change around each closed loop.
        :return: list of loop voltage sums
        """
        loopVoltages = []
        for L in self.Loops:
            loopDeltaV = 0.0
            for n in range(len(L.Nodes)):
                if n == len(L.Nodes) - 1:
                    name = L.Nodes[n] + L.Nodes[0]
                else:
                    name = L.Nodes[n] + L.Nodes[n + 1]
                loopDeltaV += self.GetElementDeltaV(name)
            loopVoltages.append(loopDeltaV)
        return loopVoltages

    def GetResistorByName(self, name):
        for r in self.Resistors:
            if r.Name == name:
                return r
        raise ValueError(f"No resistor named {name}")
    #endregion


class ResistorNetwork_2(ResistorNetwork):
    #region constructor
    def __init__(self):
        super().__init__()
    #endregion

    #region methods
    def AnalyzeCircuit(self):
        """
        Use fsolve to find currents in the modified resistor network.
        Unknowns are the currents labeled I1, I2, I3, I4, I5 on the homework figure.
        """
        i0 = [1.0, 1.0, 1.0, 1.0, 1.0]
        i = fsolve(self.GetKirchoffVals, i0)
        print(f"I1 = {i[0]:0.4f} A")
        print(f"I2 = {i[1]:0.4f} A")
        print(f"I3 = {i[2]:0.4f} A")
        print(f"I4 = {i[3]:0.4f} A")
        print(f"I5 = {i[4]:0.4f} A")
        return i

    def GetKirchoffVals(self, i):
        """
        Modified circuit equations.
        Current directions match the arrows on the right-hand homework figure:
        I1: a -> b
        I2: d -> f
        I3: c -> d
        I4: e -> d (diagonal 5 ohm resistor)
        I5: e -> c
        """
        I1, I2, I3, I4, I5 = i

        self.GetResistorByName('ad').Current = -I1  # actual current is d -> a
        self.GetResistorByName('bc').Current = I1   # actual current is b -> c
        self.GetResistorByName('cd').Current = I3   # actual current is c -> d
        self.GetResistorByName('de').Current = -I4  # actual current is e -> d
        self.GetResistorByName('df').Current = I2   # actual current is d -> f
        self.GetResistorByName('ce').Current = -I5  # actual current is e -> c

        KVL = self.GetLoopVoltageDrops()  # 3 loop equations
        Node_c_Current = I1 + I5 - I3
        Node_d_Current = I3 + I4 - I1 - I2
        KVL.append(Node_c_Current)
        KVL.append(Node_d_Current)
        return KVL
    #endregion
#endregion
