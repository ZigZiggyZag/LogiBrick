from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import constants
import sys

class Component(QGraphicsRectItem):
    def __init__(self, x, y, name, function):
        self.width = 80
        self.height = 50
        super().__init__(0, 0, self.width, self.height)
        self.setPos(x, y)
        
        self.uniqueName = name

        # Component Label
        label = QGraphicsTextItem(function, self)
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
        self.normal_brush = QBrush(QColor(100, 150, 255))

        self.setBrush(self.normal_brush)
        self.setPen(QPen(Qt.black, 2))

        # Flags
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

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
    def __init__(self):
        super().__init__()
        self.mainView = None

        # Panning variables
        self.panning = False
        self.lastPanPos = None

        # Component variables
        self.heldComponent = None

    def setMainView(self):
        self.mainView = self.views()[0]

    def addComponent(self, component: QGraphicsItem):
        self.heldComponent = component
        self.addItem(component)

    def mousePressEvent(self, event):
        match event.button():
            case Qt.MiddleButton:
                self.panning = True
                self.lastPanPos = event.screenPos()
                event.accept()
            case Qt.RightButton:
                print("TODO")
            case Qt.LeftButton:
                super().mousePressEvent(event)
            case _:
                event.accept()
    
    def mouseMoveEvent(self, event):
        if self.heldComponent:
            self.heldComponent.setPos(event.scenePos().x() - 30, event.scenePos().y() - 20)
        elif self.panning and self.lastPanPos:
            delta = event.screenPos() - self.lastPanPos
            self.lastPanPos = event.screenPos()
            self.mainView.horizontalScrollBar().setValue(self.mainView.horizontalScrollBar().value() - delta.x())
            self.mainView.verticalScrollBar().setValue(self.mainView.verticalScrollBar().value() - delta.y())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.heldComponent:
            self.heldComponent = None
            event.accept()
        elif event.button() == Qt.MiddleButton and self.panning:
            self.panning = False
            self.lastPanPos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        
            

class CircuitDesignerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogiBrick")
        self.setGeometry(100, 100, 1200, 720)

        # Main Designer View
        self.scene = CircuitDesignerScene()
        self.scene.setSceneRect(0, 0, 5000, 5000)
        self.view = CircuitDesignerView(self.scene)
        self.scene.setMainView()

        # Sidebar
        sidebar = QWidget()
        sidebarLayout = QVBoxLayout()

        for function in constants.logicFunctions:
            tempButton = QPushButton(function)
            tempButton.pressed.connect(lambda checked=None, x=function: self.createComponent(x))
            sidebarLayout.addWidget(tempButton)
        sidebarLayout.addStretch()

        sidebar.setLayout(sidebarLayout)

        # Main Layout
        mainWidget = QWidget()
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(self.view)
        mainWidget.setLayout(mainLayout)

        self.setCentralWidget(mainWidget)

        # Variables
        self.numOfEachFunction = {}
    
    def setUniqueName(self, functionName):
        if functionName in self.numOfEachFunction.keys():
            self.numOfEachFunction[functionName] = self.numOfEachFunction[functionName] + 1
        else:
            self.numOfEachFunction[functionName] = 1
        return functionName + str(self.numOfEachFunction[functionName])

    def createComponent(self, functionName):
        component = Component(0, 0, self.setUniqueName(functionName), functionName)
        self.scene.addComponent(component)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircuitDesignerWindow()
    window.show()
    sys.exit(app.exec_())