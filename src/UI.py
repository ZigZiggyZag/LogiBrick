from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import constants
import Logic
import sys

class ComponentPin(QGraphicsItem):
    def __init__(self, x, y, isInput, parent=None, pinIndex=None):
        super().__init__(parent)
        self.parent = parent
        self.setPos(x, y)
        self.isInput = isInput
        self.pinSize = 15
        self.pinIndex = pinIndex

        # Set color based on pin type
        if isInput:
            self.normalBrush = QBrush(QColor(200, 50, 50))  # Red for input
            self.hoverBrush = QBrush(QColor(255, 100, 100))
        else:
            self.normalBrush = QBrush(QColor(50, 50, 200))  # Blue for output
            self.hoverBrush = QBrush(QColor(100, 100, 255))
        
        self.currentBrush = self.normalBrush
        self.pen = QPen(Qt.black, 2)
        self.setAcceptHoverEvents(True)

        # list of connected wires
        self.wires = []

    def addWire(self, wire):
        self.wires.append(wire)
        if self.isInput:
            self.updateAssociatedInputBox()
    
    def removeWire(self, wire):
        self.wires.remove(wire)
        if self.isInput:
            self.updateAssociatedInputBox()

    def boundingRect(self):
        return QRectF(-self.pinSize/2, -self.pinSize/2, self.pinSize, self.pinSize)
    
    def paint(self, painter, option, widget):
        painter.setBrush(self.currentBrush)
        painter.setPen(self.pen)

        if self.isInput:
            painter.drawRect(self.boundingRect())
        else:
            painter.drawEllipse(self.boundingRect())
    
    def hoverEnterEvent(self, event):
        self.currentBrush = self.hoverBrush
        if (hasattr(self.parent, 'setHighlight')):
            self.parent.setHighlight(0)
        self.update()
        
    def hoverLeaveEvent(self, event):
        self.currentBrush = self.normalBrush
        if (hasattr(self.parent, 'setHighlight')):
            self.parent.setHighlight(1)
        self.update()
        
    def scenePos(self):
        return self.mapToScene(self.boundingRect().center())
    
    def getConnectedComponents(self):
        connectedComponents = []
        if len(self.wires) > 0:
            for wire in self.wires:
                wire: Wire
                sourcePin = wire.startPin if wire.startPin != self else wire.endPin
                if sourcePin and sourcePin.parentItem():
                    sourceComponent = sourcePin.parentItem()
                    if hasattr(sourceComponent, 'uniqueName'):
                        connectedComponents.append(sourceComponent)
        return connectedComponents

    def updateAssociatedInputBox(self):
        if self.isInput and (self.pinIndex is not None) and self.parentItem():
            parentComponent: Component = self.parentItem()
            connectedComponents = self.getConnectedComponents()
            if len(connectedComponents) > 0:
                combinedNames = " + ".join([f"{component.uniqueName}" for component in connectedComponents])
                parentComponent.disableInputBox(self.pinIndex, combinedNames)
            else:
                parentComponent.enableInputBox(self.pinIndex)
            
    
    def clearAllWires(self):
        wire: Wire
        for wire in self.wires[:]:
            wire.removeFromPins()
            if wire.scene():
                wire.scene().removeItem(wire)

class Wire(QGraphicsItem):
    def __init__(self, startPin: ComponentPin, endPin: ComponentPin=None, startPos=None):
        super().__init__()
        self.startPin = startPin
        self.endPin = endPin

        self.normalPen = QPen(QColor(200, 50, 50), 3)
        self.hoverPen = QPen(QColor(255, 100, 100), 5)
        self.currentPen = self.normalPen

        self.setZValue(-1)
        self.setAcceptHoverEvents(True)

        if startPin:
            startPin.addWire(self)
        if endPin:
            endPin.addWire(self)
        
        self.path = QPainterPath()
        if startPos and startPin:
            start = startPin.scenePos()
            self.updatePath(start, startPos)
        else:
            self.updatePosition()

    def boundingRect(self):
        # Add some padding for the pen width
        return self.path.boundingRect().adjusted(-5, -5, 5, 5)
    
    def shape(self):
        # Create a wider shape for easier mouse interaction
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(self.path)
    
    def setHighlight(self, highlight):
        match highlight:
            case 0: self.currentPen = self.normalPen
            case 1: self.currentPen = self.hoverPen

    def paint(self, painter, option, widget):
        painter.setPen(self.currentPen)
        painter.drawPath(self.path)
    
    def hoverEnterEvent(self, event):
        self.setHighlight(1)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setHighlight(0)
        super().hoverLeaveEvent(event)

    def updatePath(self, start, end):
        """Create a curved S-shaped path from start to end"""
        
        if (self.startPin.isInput):
            newStart = end
            newEnd = start
        else:
            newStart = start
            newEnd = end

        self.path = QPainterPath()
        self.path.moveTo(newStart)
        
        # Calculate control points for bezier curve
        dx = newEnd.x() - newStart.x()
        
        # Control points create an S-curve
        # The amount of horizontal offset determines the curve intensity
        offset = abs(dx) * 0.5
        
        ctrl1 = QPointF(newStart.x() + offset, newStart.y())
        ctrl2 = QPointF(newEnd.x() - offset, newEnd.y())
        
        # Draw cubic bezier curve
        self.path.cubicTo(ctrl1, ctrl2, newEnd)
        
        self.prepareGeometryChange()

    def updatePosition(self):
        """Update wire position based on pin positions"""
        if self.startPin:
            start = self.startPin.scenePos()
            if self.endPin:
                end = self.endPin.scenePos()
            else:
                # If no end pin, keep current endpoint
                end = self.path.currentPosition()
            self.updatePath(start, end)
            
    def setEndPoint(self, point):
        """Set temporary endpoint while dragging"""
        if self.startPin:
            start = self.startPin.scenePos()
            self.updatePath(start, point)

    def removeFromPins(self):
        if self.startPin and (self in self.startPin.wires):
            if self.endPin and self.startPin.isInput:
                if (self.endPin.parent.function == "EQN"):
                    self.startPin.parent.updateLogicBlock(self.startPin.pinIndex, self.endPin.parent.equationBlock.variableNames[self.startPin.pinIndex], True)
                else:
                    self.startPin.parent.updateLogicBlock(self.startPin.pinIndex, self.endPin.parent.uniqueName, True)
            self.startPin.removeWire(self)
        if self.endPin and (self in self.endPin.wires):
            if self.startPin and self.endPin.isInput:
                if (self.startPin.parent.function == "EQN"):
                    self.endPin.parent.updateLogicBlock(self.endPin.pinIndex, self.startPin.parent.equationBlock.variableNames[self.endPin.pinIndex], True)
                else:
                    self.endPin.parent.updateLogicBlock(self.endPin.pinIndex, self.startPin.parent.uniqueName, True)
            self.endPin.removeWire(self)

class customProxyExtension(QGraphicsProxyWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.parent = parent
        self.setAcceptHoverEvents(True)

    def setConnectedComponentHighlight(self, highlight):
        parentComponent: Component = self.parent
        connectedComponents = parentComponent.inputPins[self.index].getConnectedComponents()
        for component in connectedComponents:
            component.setHighlight(highlight)

    def hoverEnterEvent(self, event):
        parentComponent: Component = self.parent
        if (hasattr(parentComponent, 'setHighlight')):
            parentComponent.setHighlight(0)
        if (parentComponent.inputBoxes[self.index].isReadOnly):
            self.setConnectedComponentHighlight(1)
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        parentComponent: Component = self.parent
        if (hasattr(parentComponent, 'setHighlight')):
            parentComponent.setHighlight(1)
        if (parentComponent.inputBoxes[self.index].isReadOnly):
            self.setConnectedComponentHighlight(0)
        super().hoverLeaveEvent(event)

class Component(QGraphicsRectItem):
    def __init__(self, x, y, name, function, logicData: Logic.LogicData):
        self.logicData = logicData
        self.function = function

        self.variableToIndex = {}

        self.equationBlock: Logic.EquationBlock = None
        self.outputBlockName = None
        if self.function == "EQN":
            self.equationBlock: Logic.EquationBlock = self.logicData.equationBlocks[name]
            numInputs = len(self.equationBlock.variableNames)
            self.outputBlockName = self.equationBlock.outputBlockName
        else:
            numInputs = (2 if (self.function in constants.functionsWithTwoInputs) else 1)

        heightOffset = 30 if (self.function == "EQN") else 0
        heightOffset2 = 20 if (self.function == "EQN") else 0

        self.width = 100
        self.height = 80 + heightOffset + heightOffset2 + (numInputs - 1) * 30
        super().__init__(0, 0, self.width, self.height)
        self.setPos(x, y)
        self.uniqueName = name

        # Component Label
        label = QGraphicsTextItem(self.uniqueName, self)
        label.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        label.setFont(font)
        # Center the text at the top
        text_width = label.boundingRect().width()
        label.setPos((self.width - text_width) / 2, 2)
        label.setTextInteractionFlags(Qt.NoTextInteraction)

        # Colors
        self.normalBrush = QBrush(QColor(100, 150, 255))
        self.hoverBrush = QBrush(QColor(150, 200, 255))
        self.setBrush(self.normalBrush)
        self.setPen(QPen(Qt.black, 2))

        # Flags
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Extra Input Box for Equation

        if self.function == "EQN":
            equationBox = QGraphicsTextItem(self.equationBlock.equation, self)
            equationBox.setDefaultTextColor(Qt.black)
            font2 = QFont()
            font2.setPointSize(6)
            equationBox.setFont(font)
            text_width2 = equationBox.boundingRect().width()
            equationBox.setPos((self.width - text_width2) / 2, 25)
            equationBox.setTextInteractionFlags(Qt.NoTextInteraction)

        # Input Boxes
        self.inputBoxes = []
        self.inputBoxProxies = []

        for i in range(numInputs):
            # if (self.equationBlock):
            #     self.variableToIndex[i] = self.equationBlock.variableNames[i]

            inputBox = QLineEdit()
            inputBox.setValidator(QDoubleValidator())
            inputBox.setMaximumWidth(self.width - 25)
            inputBox.setAlignment(Qt.AlignCenter)
            inputBox.setStyleSheet("background-color: white; border: 1px solid black;")
            inputBoxFont = QFont()
            inputBoxFont.setBold(True)
            inputBox.setFont(inputBoxFont)

            # Update Logic Data is input set
            inputBox.editingFinished.connect(lambda checked=None, text=inputBox.text(), i=i: self.updateLogicBlock(i))
            
            proxy = customProxyExtension(i, self)
            proxy.setWidget(inputBox)
            proxy.setPos(10, 28 + heightOffset + (i * 30))

            self.inputBoxes.append(inputBox)
            self.inputBoxProxies.append(proxy)

        # Pins
        self.outpuPin = ComponentPin(self.width, self.height/2, False, self)
        
        self.inputPins = []

        for i in range(numInputs):
            pinYPos = (37 + heightOffset + (i * 30))
            pin = ComponentPin(0, pinYPos, True, self, i)
            self.inputPins.append(pin)
        
        # Checkboxes

        if (self.function == "EQN"):
            checkbox1 = QCheckBox("Sep. Out")
            checkbox1.setFont(font)
            checkbox1.stateChanged.connect(self.setEQNOutSeparate)
            checkbox1.setStyleSheet("background-color: transparent; color: white;")

            proxy = QGraphicsProxyWidget(self)
            proxy.setWidget(checkbox1)
            proxy.setPos(10, 25 + heightOffset + (numInputs * 30))

            checkbox2 = QCheckBox("Sep. Var")
            checkbox2.stateChanged.connect(self.setEQNVarSeparate)
            checkbox2.setFont(font)
            checkbox2.setStyleSheet("background-color: transparent; color: white;")

            proxy = QGraphicsProxyWidget(self)
            proxy.setWidget(checkbox2)
            proxy.setPos(10, 45 + heightOffset + (numInputs * 30))
        else:
            checkbox = QCheckBox("Separate")
            checkbox.stateChanged.connect(self.setSeparate)
            checkbox.setFont(font)
            checkbox.setStyleSheet("background-color: transparent; color: white;")

            proxy = QGraphicsProxyWidget(self)
            proxy.setWidget(checkbox)
            proxy.setPos(10, 25 + heightOffset + (numInputs * 30))

    def setHighlight(self, highlight):
        match highlight:
            case 0: self.setBrush(self.normalBrush)
            case 1: self.setBrush(self.hoverBrush)

    def hoverEnterEvent(self, event):
        self.setHighlight(1)
        super().hoverEnterEvent(event)
    
    def hoverMoveEvent(self, event):
        super().hoverMoveEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.setHighlight(0)
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for pin in self.inputPins:
                for wire in pin.wires:
                    wire.updatePosition()
            for wire in self.outpuPin.wires:
                wire.updatePosition()
        return super().itemChange(change, value)
    
    def disableInputBox(self, inputBoxIndex, text=""):
        inputBox:QLineEdit = self.inputBoxes[inputBoxIndex]
        inputBox.setReadOnly(True)
        inputBox.setStyleSheet("background-color: #cccccc; border: 1px solid black;")
        inputBox.setText(text)

    def enableInputBox(self, inputBoxIndex):
        inputBox:QLineEdit = self.inputBoxes[inputBoxIndex]
        inputBox.setReadOnly(False)
        inputBox.setStyleSheet("background-color: white; border: 1px solid black;")
        inputBox.setText("")  # Clear the text when disconnected

    def setSeparate(self, state):
        print("setSeparate Called")
        self.logicData.separateLogicBlock(self.uniqueName, (state==2))
    
    def setEQNOutSeparate(self, state):
        self.logicData.separateLogicBlock(self.equationBlock.outputBlockName, (state==2))
    
    def setEQNVarSeparate(self, state):
        for variableName in self.equationBlock.variableNames:
            self.logicData.separateLogicBlock(variableName, (state==2))

    def updateLogicBlock(self, index, text=None, remove=False):
        if (self.function == "EQN"):
            if text:
                self.logicData.updateLogicBlock(self.equationBlock.variableNames[index], inputA=text, inputB = 0, remove=remove)
            else:
                self.logicData.updateLogicBlock(self.equationBlock.variableNames[index], inputA=self.inputBoxes[index].text(), inputB = 0)
        else:
            if text:
                if index == 0:
                    self.logicData.updateLogicBlock(self.uniqueName, inputA=text, remove=remove)
                else:
                    self.logicData.updateLogicBlock(self.uniqueName, inputB=text, remove=remove)
            else:
                if index == 0:
                    self.logicData.updateLogicBlock(self.uniqueName, inputA=self.inputBoxes[index].text())
                else:
                    self.logicData.updateLogicBlock(self.uniqueName, inputB=self.inputBoxes[index].text())
    
    def removeFromScene(self):
        pin: ComponentPin
        for pin in self.inputPins:
            pin.clearAllWires()
        self.outpuPin.clearAllWires()


class CircuitDesignerView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.zoomFactor = 1.15

    # scrool wheel zoom
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale(self.zoomFactor, self.zoomFactor)
        else:
            self.scale(1/self.zoomFactor, 1/self.zoomFactor)

class CircuitDesignerScene(QGraphicsScene):
    def __init__(self, logicData: Logic.LogicData):
        super().__init__()
        self.mainView = None

        # Panning variables
        self.panning = False
        self.lastPanPos = None

        # Component variables
        self.heldComponent = None

        # Wire variables
        self.heldWire = None
        self.drawingWire = False

        # Logic Data
        self.logicData = logicData

    def setMainView(self):
        self.mainView = self.views()[0]

    def addComponent(self, functionName):
        logicBlock: Logic.LogicBlock = self.logicData.addLogicBlock(functionName)
        component = Component(0, 0, logicBlock.name, functionName, self.logicData)
        self.heldComponent = component
        self.addItem(component)

    def addComponentEq(self, equation):
        equationBlock: Logic.EquationBlock = self.logicData.addEquationBlock(equation)
        component = Component(0, 0, equationBlock.name, "EQN", self.logicData)
        self.heldComponent = component
        self.addItem(component)

    def startWire(self, startPin: ComponentPin, startPos: QPointF):
        self.drawingWire = True
        self.heldWire = Wire(startPin=startPin, startPos=startPos)
        self.addItem(self.heldWire)

    def finishWire(self, startPin: ComponentPin, endPin: ComponentPin):
        # Check if the pin clicked on is not the same pin we started on
        notStartPin = (endPin != startPin)
        # Make sure only one of the pins is an input pin
        validConnection = (startPin.isInput != endPin.isInput)
        # Make sure the connection is unique
        uniqueConnection = True
        for wire in startPin.wires:
            if wire.endPin == endPin or wire.startPin == endPin:
                uniqueConnection = False
                break
        # Make sure the clicked pin is not attached to the same component
        notSameParent = (startPin.parent != endPin.parent)

        if notStartPin and validConnection and uniqueConnection and notSameParent:
            self.heldWire.endPin = endPin
            endPin.addWire(self.heldWire)
            self.heldWire.updatePosition()
            if startPin.parent.function == "EQN":
                if startPin.isInput:
                    startPin.updateAssociatedInputBox()
                    if endPin.parent.function == "EQN":
                        print("startPin is EQN, endPin is EQN")
                        startPin.parent.updateLogicBlock(startPin.pinIndex, endPin.parent.outputBlockName)
                    else:
                        print("startPin is EQN, endPin is not EQN")
                        startPin.parent.updateLogicBlock(startPin.pinIndex, endPin.parent.uniqueName)
                else:
                    print ("test1")
                    endPin.parent.updateLogicBlock(endPin.pinIndex, startPin.parent.outputBlockName)
            else:
                if startPin.isInput:
                    startPin.updateAssociatedInputBox()
                    if endPin.parent.function == "EQN":
                        print("startPin is not EQN, endPin is EQN")
                        startPin.parent.updateLogicBlock(startPin.pinIndex, endPin.parent.outputBlockName)
                    else:
                        print("startPin is not EQN, endPin is not EQN")
                        startPin.parent.updateLogicBlock(startPin.pinIndex, endPin.parent.uniqueName)
                else:
                    print ("test2")
                    endPin.parent.updateLogicBlock(endPin.pinIndex, startPin.parent.uniqueName)
            self.drawingWire = False
            self.heldWire = None
        else:
            self.cancelWire()

    def cancelWire(self):
        self.heldWire.removeFromPins()
        self.removeItem(self.heldWire)
        self.drawingWire = False
        self.heldWire = None

    def removeComponent(self, component: Component):
        component.removeFromScene()
        if (component.function == "EQN"):
            self.logicData.removeEquationBlock(component.uniqueName)
        else:
            self.logicData.removeLogicBlock(component.uniqueName)
        self.removeItem(component)

    def removeWire(self, wire: Wire):
        wire.removeFromPins()
        self.removeItem(wire)
        if self.heldWire:
            self.drawingWire = False
            self.heldWire = None
    
    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform())

        match event.button():
            case Qt.MiddleButton:
                self.panning = True
                self.lastPanPos = event.screenPos()
                event.accept()
            case Qt.RightButton:
                event.accept()
            case Qt.LeftButton:
                if (isinstance(item, ComponentPin)):
                    if (not self.drawingWire):
                        self.startWire(item, event.scenePos())
                        super().mousePressEvent(event)
                    else:
                        self.finishWire(self.heldWire.startPin, item)
                        event.accept()   
                elif self.heldWire:
                    self.cancelWire()
                    event.accept()  
                else:
                    super().mousePressEvent(event)
            case _:
                event.accept()
    
    def mouseMoveEvent(self, event):
        if self.heldComponent:
            self.heldComponent.setPos(event.scenePos().x() - (self.heldComponent.width / 2), event.scenePos().y() - (self.heldComponent.height / 2))
        elif self.panning and self.lastPanPos:
            delta = event.screenPos() - self.lastPanPos
            self.lastPanPos = event.screenPos()
            self.mainView.horizontalScrollBar().setValue(self.mainView.horizontalScrollBar().value() - delta.x())
            self.mainView.verticalScrollBar().setValue(self.mainView.verticalScrollBar().value() - delta.y())
        elif self.drawingWire and self.heldWire:
            self.heldWire.setEndPoint(event.scenePos())
            super().mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform())

        # If we clicked on a child item (like label or pin), get the parent component
        if isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), Component):
            itemComponent = item.parentItem()
        elif isinstance(item, Component):
            itemComponent = item
        else:
            itemComponent = None

        if self.heldComponent:
            self.heldComponent = None
            event.accept()
        elif event.button() == Qt.MiddleButton and self.panning:
            self.panning = False
            self.lastPanPos = None
            event.accept()
        elif event.button() == Qt.RightButton:
            if itemComponent:
                self.removeComponent(itemComponent)
                event.accept()
            elif isinstance(item, Wire):
                self.removeWire(item)
                event.accept()
            else:
                event.accept()
        else:
            super().mouseReleaseEvent(event)
        
            

class CircuitDesignerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogiBrick")
        self.setGeometry(100, 100, 1200, 720)

        # Logic Data
        self.logicData = Logic.LogicData()

        # Converter
        self.converter = Logic.LogicExporter("Test Generated", self.logicData.logicData)

        # Main Designer View
        self.scene = CircuitDesignerScene(self.logicData)
        self.scene.setSceneRect(0, 0, 5000, 5000)
        self.view = CircuitDesignerView(self.scene)
        self.scene.setMainView()

        # Sidebar
        sidebar = QWidget()
        sidebarLayer1 = QVBoxLayout()
        sidebarLayer2 = QHBoxLayout()
        sidebarLayer3_1 = QVBoxLayout()
        sidebarLayer3_2 = QVBoxLayout()

        i = 0
        for function in constants.logicFunctions:
            tempButton = QPushButton(function)
            tempButton.pressed.connect(lambda checked=None, functionName=function: self.scene.addComponent(functionName))
            if i < (len(constants.logicFunctions)/2):
                sidebarLayer3_1.addWidget(tempButton)
            else:
                sidebarLayer3_2.addWidget(tempButton)
            i += 1
        sidebarLayer3_1.addStretch()
        sidebarLayer3_2.addStretch()

        sidebarLayer2.addLayout(sidebarLayer3_1)
        sidebarLayer2.addLayout(sidebarLayer3_2)

        generateButton = QPushButton("Generate")
        generateButton.pressed.connect(self.generateCreation)

        equationButton = QPushButton("Equation")
        equationButton.pressed.connect(self.equationPopup)

        sidebarLayer1.addWidget(generateButton)
        sidebarLayer1.addItem(QSpacerItem(0, 15, QSizePolicy.Fixed, QSizePolicy.Minimum))
        sidebarLayer1.addWidget(equationButton)
        sidebarLayer1.addLayout(sidebarLayer2)

        sidebar.setLayout(sidebarLayer1)
        sidebar.setMaximumWidth(300)

        # Main Layout
        mainWidget = QWidget()
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(self.view)
        mainWidget.setLayout(mainLayout)

        self.setCentralWidget(mainWidget)

    def equationPopup(self):
        text, ok = QInputDialog.getText(self, 'Equation', 'Enter Equation: ')

        if ok and text:
            self.scene.addComponentEq(text)
        elif ok:
            QMessageBox.warning(self, 'Error!', 'Please enter equation!')

    def generateCreation(self):
        self.converter.convertLogicDataToCreation()
        self.converter.exportCreation()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircuitDesignerWindow()
    window.show()
    sys.exit(app.exec_())