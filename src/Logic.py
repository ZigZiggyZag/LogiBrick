import constants
import BRCI

import pprint

class LogicBlock:
    def __init__(self, name, function, inputA=1, inputB=1):
        self.name = name
        self.function = function
        self.inputA = None
        self.inputB = None
        self.updateInputs(inputA, inputB)

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
        
    def generateUniqueName(self, name):
        if name in self.numOfEachFunction.keys():
            self.numOfEachFunction[name] = self.numOfEachFunction[name] + 1
        else:
            self.numOfEachFunction[name] = 1
        return name + str(self.numOfEachFunction[name])
        
    def printLogicData(self):
        print("--------------------------------------")
        printable_dict = {k: str(v) for k, v in self.logicData.items()}
        pprint.pprint(printable_dict)
    
    def addLogicBlock(self, function, inputA=1, inputB=1, customName=None):
        if (not customName):
            name = self.generateUniqueName(function)
            logicBlock = LogicBlock(name, function, inputA, inputB)
            self.logicData[name] = logicBlock
        else:
            name = self.generateUniqueName(customName)
            logicBlock = LogicBlock(customName, function, inputA, inputB)
            self.logicData[customName] = logicBlock

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

class EquationBlockConverter:
    def __init__(self, logicData: LogicData):
        self.logicData = logicData

    def tokenToFunctionName(self, token: str):
        if token in constants.tokenToFuncName.keys():
            return constants.tokenToFuncName[token]
        elif token in constants.logicFunctions:
            return token
        else:
            return None

    def isFunctionNotOperator(self, token: str):
        return ((token not in constants.tokenToFuncName.keys()) and (token not in constants.tokenToFuncName.values())) and (token in constants.logicFunctions)
    
    def isOperatorNotFunction(self, token: str):
        return (token not in constants.logicFunctions) and (token in constants.tokenToFuncName.keys())

    def isNotFunctionOperator(self, token: str):
        return ((token not in constants.tokenToFuncName.keys()) and (token not in constants.logicFunctions))

    def manageImplicitMultipication(self, inputEquation: str):
        splitEquation = inputEquation.split(' ')
        outputEquation = splitEquation[0]
        for i in range(len(splitEquation) - 1):
            if (((splitEquation[i+1] == '(') and (splitEquation[i] != '(') and (self.isNotFunctionOperator(splitEquation[i]))) or 
                ((splitEquation[i] == ')') and (splitEquation[i+1] != ')') and (self.isNotFunctionOperator(splitEquation[i+1])))):
                outputEquation += " *"
            outputEquation += (" " + splitEquation[i + 1])
        return outputEquation
    
    def shuntingYard(self, inputEquation: str):
        outputQueue = []
        operatorStack = []

        modifiedEquation = self.manageImplicitMultipication(inputEquation)

        for token in modifiedEquation.split(' '):
            if self.isOperatorNotFunction(token):
                while((len(operatorStack) > 0) and 
                    (operatorStack[-1] != "(") and 
                    ((constants.precedence[token] < constants.precedence[operatorStack[-1]]) or ((token != "^") and (constants.precedence[token] == constants.precedence[operatorStack[-1]])))):
                    outputQueue.append(operatorStack.pop())
                operatorStack.append(token)
            elif self.isFunctionNotOperator(token):
                operatorStack.append(token)
            elif token == ",":
                while((len(operatorStack) > 0) and (operatorStack[-1] != "(")):
                    outputQueue.append(operatorStack.pop())
            elif token == "(":
                operatorStack.append(token)
            elif token == ")":
                while((len(operatorStack) > 0) and (operatorStack[-1] != "(")):
                    outputQueue.append(operatorStack.pop())
                if (operatorStack[-1] == "("):
                    operatorStack.pop()
                if ((len(operatorStack) > 0) and (operatorStack[-1] in constants.functionNames)):
                    outputQueue.append(operatorStack.pop())
            else:
                outputQueue.append(token)

        while (len(operatorStack) > 0):
            outputQueue.append(operatorStack.pop())
        
        return outputQueue
    
    def generateLogicBlocks(self, equation: str):
        revPolNoEq = self.shuntingYard(equation)
        
        evaluationStack = []
        variables = []

        for token in revPolNoEq:
            if (self.isNotFunctionOperator(token)):
                evaluationStack.append(token)
                if (isinstance(self.logicData.makeNumberifNumber(token), str) and not (token in variables)):
                    variables.append(token)
                    self.logicData.addLogicBlock("ADD", custonName=token)
            elif (token != "MIN" and token != "MAX") and self.isFunctionNotOperator(token):
                blockName = self.tokenToFunctionName(token)
                logicBlock = self.logicData.addLogicBlock(blockName, evaluationStack.pop())
                evaluationStack.append(logicBlock.name)
            else:
                blockName = self.tokenToFunctionName(token)
                opB = evaluationStack.pop()
                opA = evaluationStack.pop()
                logicBlock = self.logicData.addLogicBlock(blockName, opA, opB)
                evaluationStack.append(logicBlock.name)

        #generateMathBrick(creation, "FinalOutput", "Add", makeNumberifNumber(evaluationStack.pop()), 0, y = -10)
        #generateTextBrick(creation, "FullEquation", equation, x = 10, z = 5, zrot = -90)


class LogicExporter:
    def __init__(self, name, logicData: LogicData):
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