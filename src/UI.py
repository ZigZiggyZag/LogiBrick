from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class CircuitDesignerView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
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
        self.panning = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = True

class CircuitDesignerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogiBrick")
        self.setGeometry(100, 100, 1200, 720)

        # Main Designer View
        self.scene = CircuitDesignerScene()
        self.scene.setSceneRect(0, 0, 5000, 5000)
        self.view = CircuitDesignerView(self.scene)

        # Sidebar
        sidebar = QWidget()
        sidebarLayout = QVBoxLayout()

        buttonNames = ["ADD", "SUB", "MULT", "DIV", "MOD", "POWER", "GREATER", 
                       "LESS", "MIN", "MAX", "ABS", "SIGN", "ROUND", "CEIL",
                       "FLOOR", "SQRT", "dSIN", "dASIN", "dCOS", "dACOS", "dTAN",
                       "dATAN", "rSIN", "rASIN", "rCOS", "rACOS", "rTAN", "rATAN"]

        for name in buttonNames:
            tempButton = QPushButton(name)
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircuitDesignerWindow()
    window.show()
    sys.exit(app.exec_())