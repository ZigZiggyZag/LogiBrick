import constants
import BRCI

import pprint

class LogicExporter:
    def __init__(self, name, logicData):
        self.creation: BRCI.ModernCreation = BRCI.Creation14(
            project_name=name,
            project_dir=BRCI.ModernCreation.get_brick_rigs_vehicle_folder()
        )
        self.logicData = logicData
    
    def generateMathBrick(self, brickName: str, operation: str, inputA: float | int | str, inputB: float | int | str = 1.0, x = 0, y = 0, z = 0):
        self.creation.add_brick(
            'MathBrick_1sx1sx1s',
            brickName,
            position=[x, y, z],
            rotation=[0, 0, 0],
            properties={
                "Operation": operation,
                "InputChannelA.InputAxis" : ("Custom" if isinstance(inputA, str) else "AlwaysOn"),
                "InputChannelA.SourceBricks": (([inputA] if inputA != "None" else []) if isinstance(inputA, str) else []),
                "InputChannelA.Value": (inputA if isinstance(inputA, (int, float)) else 1),
                "InputChannelB.InputAxis" : ("Custom" if isinstance(inputB, str) else "AlwaysOn"),
                "InputChannelB.SourceBricks": (([inputB] if inputB != "None" else []) if isinstance(inputB, str) else []),
                "InputChannelB.Value": (inputB if isinstance(inputB, (int, float)) else 1)
            }
        )

    def generateSwitchBrick(self, brickName: str, minIn: int | float = -1.0, maxIn: int | float = 1.0, minOut: int | float = -1.0, maxOut: int | float = 1.0, input: str = "None", x = 0, y = 0, z = 0):
        self.creation.add_brick(
            'Switch_1sx1sx1s',
            brickName,
            position=[x, y, z],
            rotation=[0, 0, 0],
            properties={
                "OutputChannel.MinIn" : minIn,
                "OutputChannel.MaxIn": maxIn,
                "OutputChannel.MinOut": minOut,
                "OutputChannel.MaxOut" : maxOut,
                "InputChannel.InputAxis": input,
                "InputChannelB.SourceBricks": ([input] if input != "None" else [])
            }
        )

    def generateTextBrick(self, brickName: str, text: str, x = 0, y = 0, z = 0, xrot = 0, yrot = 0, zrot = 0):
        self.creation.add_brick(
            'TextBrick',
            brickName,
            position=[x, y, z],
            rotation=[xrot, yrot, zrot],
            properties={
                "BrickSize" : [1.0, 1.0, 1.0],
                "Text" : text
            }
        )

    def convertLogicDataToCreation(self):
        print("TODO")
    
    def exportCreation(self):
        self.creation.write_creation(exist_ok=True)
        self.creation.write_metadata(exist_ok=True)

class LogicBlock:
    def __init__(self, name, function, inputA=1, inputB=1):
        self.name = name
        self.function = function
        self.inputA = inputA
        self.inputB = inputB

    def __str__(self):
        return f"[Name: {self.name}, Function: {self.function}, inputA: {self.inputA}, inputB: {self.inputB}]"

    def updateInputs(self, inputA=None, inputB=None):
        if inputA:
            if isinstance(inputA, str):
                if not isinstance(self.inputA, list) or len(self.inputA) == 0:
                    self.inputA = [inputA]
                else:
                    self.inputA.append(inputA)
            else:
                self.inputA = inputA
        if inputB:
            if isinstance(inputB, str):
                if not isinstance(self.inputB, list) or len(self.inputB) == 0:
                    self.inputB = [inputB]
                else:
                    self.inputB.append(inputB)
            else:
                self.inputB = inputB

    def removeInputs(self, inputA=None, inputB=None):
        print("removeInputsCalled")
        if inputA and isinstance(inputA, str) and isinstance(self.inputA, list):
            print(f"removing {inputA}")
            self.inputA.remove(inputA)
            if len(self.inputA) == 0:
                self.inputA = 1
        if inputB and isinstance(inputB, str) and isinstance(self.inputB, list):
            print(f"removing {inputB}")
            self.inputB.remove(inputB)
            if len(self.inputB) == 0:
                self.inputB = 1

class LogicData:
    def __init__(self):
        # Variables
        self.numOfEachFunction = {}
        self.logicData = {}

    def makeNumberifNumber(self, string: str):
        try:
            return float(string)
        except ValueError:
            return string
    
    def addLogicBlock(self, function, inputA=1, inputB=1):
        name = self.generateUniqueName(function)
        logicBlock = LogicBlock(name, function, inputA, inputB)
        self.logicData[name] = logicBlock

        printable_dict = {k: str(v) for k, v in self.logicData.items()}
        pprint.pprint(printable_dict)

        return logicBlock

    def updateLogicBlock(self, name, inputA=None, inputB=None, remove=False):
        inputAConverted = self.makeNumberifNumber(inputA) if inputA else None
        inputBConverted = self.makeNumberifNumber(inputB) if inputB else None

        if remove:
             self.logicData[name].removeInputs(inputAConverted, inputBConverted)
        else:
            self.logicData[name].updateInputs(inputAConverted, inputBConverted)

        printable_dict = {k: str(v) for k, v in self.logicData.items()}
        pprint.pprint(printable_dict)

    def generateUniqueName(self, functionName):
        if functionName in self.numOfEachFunction.keys():
            self.numOfEachFunction[functionName] = self.numOfEachFunction[functionName] + 1
        else:
            self.numOfEachFunction[functionName] = 1
        return functionName + str(self.numOfEachFunction[functionName])