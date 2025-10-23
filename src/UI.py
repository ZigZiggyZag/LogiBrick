from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class CircuitDesignerView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)

class CircuitDesignerScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircuitDesignerWindow()
    window.show()
    sys.exit(app.exec_())