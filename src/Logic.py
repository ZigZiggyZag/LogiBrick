import constants
import BRCI

import pprint

class LogicBlock:
    def __init__(self, name, function, inputA=1, inputB=1):
        self.name = name
        self.function = function
        self.inputA = inputA
        self.inputB = inputB

    def __str__(self):
        return f"[Name: {self.name}, Function: {self.function}, inputA: {self.inputA}, inputB: {self.inputB}]"

    def updateInputs(self, inputA=None, inputB=None):
        if inputA != None:
            if isinstance(inputA, str):
                if not isinstance(self.inputA, list) or len(self.inputA) == 0:
                    self.inputA = [inputA]
                else:
                    self.inputA.append(inputA)
            else:
                self.inputA = inputA
        if inputB != None:
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

class LogicExporter:
    def __init__(self, name, logicData):
        self.creation: BRCI.ModernCreation = BRCI.Creation14(
            project_name=name,
            project_dir=BRCI.ModernCreation.get_brick_rigs_vehicle_folder()
        )
        self.logicData = logicData
        self.convertedBlocks = []
        self.x = 0
        self.y = 0
    
    def generateMathBrick(self, brickName: str, operation: str, inputA: float | list = 1, inputB: float | list = 1, x = 0, y = 0, z = 0):
        self.creation.add_brick(
            'MathBrick_1sx1sx1s',
            brickName,
            position=[x, y, z],
            rotation=[0, 0, 0],
            properties={
                "Operation": operation,
                "InputChannelA.InputAxis" : ("Custom" if isinstance(inputA, list) else "AlwaysOn"),
                "InputChannelA.SourceBricks": (inputA if isinstance(inputA, list) else []),
                "InputChannelA.Value": (inputA if isinstance(inputA, (int, float)) else 1),
                "InputChannelB.InputAxis" : ("Custom" if isinstance(inputB, list) else "AlwaysOn"),
                "InputChannelB.SourceBricks": (inputB if isinstance(inputB, list) else []),
                "InputChannelB.Value": (inputB if isinstance(inputB, (int, float)) else 1)
            }
        )
    
    def returnAndIncrementCoordinates(self):
        oldXY = (self.x, self.y)
        self.x += 10
        if self.x == 110:
            self.x = 0
            self.y += 10
        return oldXY

    def convertLogicBlock(self, logicBlock: LogicBlock):
        if (logicBlock.name not in self.convertedBlocks):
            if (isinstance(logicBlock.inputA, list)):
                for blockName in logicBlock.inputA:
                    self.convertLogicBlock(self.logicData[blockName])
            if (isinstance(logicBlock.inputB, list)):
                for blockName in logicBlock.inputB:
                    self.convertLogicBlock(self.logicData[blockName])
            coordinates = self.returnAndIncrementCoordinates()
            self.generateMathBrick(logicBlock.name, constants.functionToBRName[logicBlock.function], logicBlock.inputA, logicBlock.inputB, coordinates[0], coordinates[1])
            self.convertedBlocks.append(logicBlock.name)

    def convertLogicDataToCreation(self):
        self.creation.bricks = []
        for block in self.logicData.values():
            if (block not in self.convertedBlocks):
                self.convertLogicBlock(block)
        print("Creation Generated")
        self.convertedBlocks = []
        self.x = 0
        self.y = 0

    def exportCreation(self):
        self.creation.write_creation(exist_ok=True)
        self.creation.write_metadata(exist_ok=True)
        print("Creation Written")

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
        
    def generateUniqueName(self, functionName):
        if functionName in self.numOfEachFunction.keys():
            self.numOfEachFunction[functionName] = self.numOfEachFunction[functionName] + 1
        else:
            self.numOfEachFunction[functionName] = 1
        return functionName + str(self.numOfEachFunction[functionName])
        
    def printLogicData(self):
        print("--------------------------------------")
        printable_dict = {k: str(v) for k, v in self.logicData.items()}
        pprint.pprint(printable_dict)
    
    def addLogicBlock(self, function, inputA=1, inputB=1):
        name = self.generateUniqueName(function)
        logicBlock = LogicBlock(name, function, inputA, inputB)
        self.logicData[name] = logicBlock

        self.printLogicData()

        return logicBlock
    
    def removeLogicBlock(self, name):
        del self.logicData[name]

        self.printLogicData()

    def updateLogicBlock(self, name, inputA=None, inputB=None, remove=False):
        inputAConverted = self.makeNumberifNumber(inputA) if inputA else None
        inputBConverted = self.makeNumberifNumber(inputB) if inputB else None

        if remove:
             self.logicData[name].removeInputs(inputAConverted, inputBConverted)
        else:
            self.logicData[name].updateInputs(inputAConverted, inputBConverted)

        self.printLogicData()