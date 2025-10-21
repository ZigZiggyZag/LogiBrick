import BRCI

functionNames = (
    "MIN",
    "MAX",
    "ABS",
    "SIGN",
    "ROUND",
    "CEIL",
    "FLOOR",
    "SQRT",
    "dSIN",
    "dASIN",
    "dCOS",
    "dACOS",
    "dTAN",
    "dATAN",
    "rSIN",
    "rASIN",
    "rCOS",
    "rACOS",
    "rTAN",
    "rATAN",
    "SIN",
    "ASIN",
    "COS",
    "ACOS",
    "TAN",
    "ATAN"
)

operators = (
    "^",
    "*",
    "/",
    "%",
    "+",
    "-",
    ">",
    "<"
)

precedence = {
    "^": 4,
    "*": 3,
    "/": 3,
    "%": 3,
    "+": 2,
    "-": 2,
    ">": 1,
    "<": 1
}

opToBROp = {
    "+": "Add",
    "-": "Subtract",
    "*": "Multiply",
    "/": "Divide",
    "%": "Fmod",
    "^": "Power",
    ">": "Greater",
    "<": "Less",
    "MIN": "Min",
    "MAX": "Max",
    "ABS": "Abs",
    "SIGN": "Sign",
    "ROUND": "Round",
    "CEIL": "Ceil",
    "FLOOR": "Floor",
    "SQRT": "Sqrt",
    "dSIN": "SinDeg",
    "rSIN": "Sin",
    "SIN": "Sin",
    "dCOS": "CosDeg",
    "rCOS": "Cos",
    "COS": "Cos",
    "dTAN": "TanDeg",
    "rTAN": "Tan",
    "TAN": "Tan",
    "dASIN": "AsinDeg",
    "rASIN": "Asin",
    "ASIN": "Asin",
    "dACOS": "AcosDeg",
    "rACOS": "Acos",
    "ACOS": "Acos",
    "dATAN": "AtanDeg",
    "rATAN": "Atan",
    "ATAN": "Atan"
}

# Enter equation here, ensure there is a space between each token
equation = '( ( SQRT ( ( dSIN ( 4 + var1 ) ) ^ 3 ) * 24 ) / 2 ) + var2'

def isNotFunctionOperator(token: str):
    return ((token not in functionNames) and (token not in operators))

def makeNumberifNumber(string: str):
    try:
        return float(string)
    except ValueError:
        return string

def manageImplicitMultipication(inputEquation: str):
    splitEquation = inputEquation.split(' ')
    outputEquation = splitEquation[0]
    for i in range(len(splitEquation) - 1):
        if (((splitEquation[i+1] == '(') and (splitEquation[i] != '(') and (isNotFunctionOperator(splitEquation[i]))) or 
            ((splitEquation[i] == ')') and (splitEquation[i+1] != ')') and (isNotFunctionOperator(splitEquation[i+1])))):
            outputEquation += " *"
        outputEquation += (" " + splitEquation[i + 1])
    return outputEquation

def shuntingYard(inputEquation: str):
    outputQueue = []
    operatorStack = []

    modifiedEquation = manageImplicitMultipication(inputEquation)

    for token in modifiedEquation.split(' '):
        if token in operators:
            while((len(operatorStack) > 0) and 
                (operatorStack[-1] != "(") and 
                ((precedence[token] < precedence[operatorStack[-1]]) or ((token != "^") and (precedence[token] == precedence[operatorStack[-1]])))):
                outputQueue.append(operatorStack.pop())
            operatorStack.append(token)
        elif token in functionNames:
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
            if ((len(operatorStack) > 0) and (operatorStack[-1] in functionNames)):
                outputQueue.append(operatorStack.pop())
        else:
            outputQueue.append(token)

    while (len(operatorStack) > 0):
        outputQueue.append(operatorStack.pop())
    
    return outputQueue

def generateMathBrick(creationObject: BRCI.Creation14, brickName: str, operation: str, inputA: float | int | str, inputB: float | int | str = 1.0, x = 0, y = 0, z = 0):
    creationObject.add_brick(
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

def generateSwitchBrick(creationObject: BRCI.Creation14, brickName: str, minIn: int | float = -1.0, maxIn: int | float = 1.0, minOut: int | float = -1.0, maxOut: int | float = 1.0, input: str = "None", x = 0, y = 0, z = 0):
    creationObject.add_brick(
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

def generateTextBrick(creationObject: BRCI.Creation14, brickName: str, text: str, x = 0, y = 0, z = 0, xrot = 0, yrot = 0, zrot = 0):
    creationObject.add_brick(
        'TextBrick',
        brickName,
        position=[x, y, z],
        rotation=[xrot, yrot, zrot],
        properties={
            "BrickSize" : [1.0, 1.0, 1.0],
            "Text" : text
        }
    )

def generateCreation(name: str, equation: str):
    creation: BRCI.ModernCreation = BRCI.Creation14(
        project_name=name,
        project_dir=BRCI.ModernCreation.get_brick_rigs_vehicle_folder()
    )

    revPolNoEq = shuntingYard(equation)
    
    evaluationStack = []
    variables = []

    xLocation = 0
    nameIterator = 0

    for token in revPolNoEq:
        if (isNotFunctionOperator(token)):
            evaluationStack.append(token)
            if (isinstance(makeNumberifNumber(token), str) and not (token in variables)):
                variables.append(token)
                generateMathBrick(creation, token, "Add", "None", 0, x = xLocation, y = 10)
                generateTextBrick(creation, token + "text", token, x = xLocation, y = 20, z = 5, zrot = -90)
                xLocation += 10
        elif ((token in functionNames) and (token != "MIN" and token != "MAX" and token != "ABS")):
            brOpName = opToBROp[token]
            tokenName = brOpName + str(nameIterator)
            nameIterator += 1
            generateMathBrick(creation, tokenName, brOpName, makeNumberifNumber(evaluationStack.pop()))
            evaluationStack.append(tokenName)
        else:
            brOpName = opToBROp[token]
            tokenName = brOpName + str(nameIterator)
            nameIterator += 1
            opB = makeNumberifNumber(evaluationStack.pop())
            opA = makeNumberifNumber(evaluationStack.pop())
            generateMathBrick(creation, tokenName, brOpName, opA, opB)
            evaluationStack.append(tokenName)

    generateMathBrick(creation, "FinalOutput", "Add", makeNumberifNumber(evaluationStack.pop()), 0, y = -10)
    generateTextBrick(creation, "FullEquation", equation, x = 10, z = 5, zrot = -90)

    creation.write_creation(exist_ok=True)  # Create the Vehicle.brv file, overwriting if required
    creation.write_metadata(exist_ok=True)  # Create the Metadata.brm file, overwriting if required

generateCreation("TestGen", equation)