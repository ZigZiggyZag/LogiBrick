from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsRectItem, QMainWindow,
                             QGraphicsItem, QGraphicsLineItem, QPushButton, QVBoxLayout,
                             QWidget, QHBoxLayout, QInputDialog, QGraphicsTextItem, QMessageBox)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QFont
import sys

class CircuitView(QGraphicsView):
    """Custom view with zoom functionality"""
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.zoom_factor = 1.15
        
    def wheelEvent(self, event):
        # Zoom in/out with scroll wheel
        if event.angleDelta().y() > 0:
            # Zoom in
            self.scale(self.zoom_factor, self.zoom_factor)
        else:
            # Zoom out
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)

class ConnectionPin(QGraphicsEllipseItem):
    """Represents a connection point on a component"""
    def __init__(self, x, y, parent=None):
        super().__init__(-5, -5, 10, 10, parent)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(50, 150, 50)))
        self.setPen(QPen(Qt.black, 2))
        self.setAcceptHoverEvents(True)
        self.wires = []
        
    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor(100, 255, 100)))
        
    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor(50, 150, 50)))
        
    def scenePos(self):
        return self.mapToScene(self.rect().center())

class Wire(QGraphicsLineItem):
    """Represents a wire connection between two pins"""
    def __init__(self, start_pin, end_pin=None, start_pos=None):
        super().__init__()
        self.start_pin = start_pin
        self.end_pin = end_pin
        self.normal_pen = QPen(QColor(200, 50, 50), 3)
        self.hover_pen = QPen(QColor(255, 100, 100), 5)
        self.setPen(self.normal_pen)
        self.setZValue(-1)
        self.setAcceptHoverEvents(True)
        
        if start_pin:
            start_pin.wires.append(self)
        if end_pin:
            end_pin.wires.append(self)
        
        # Initialize with start position if provided
        if start_pos and start_pin:
            start = start_pin.scenePos()
            self.setLine(start.x(), start.y(), start_pos.x(), start_pos.y())
        else:
            self.updatePosition()
    
    def hoverEnterEvent(self, event):
        self.setPen(self.hover_pen)
        
    def hoverLeaveEvent(self, event):
        self.setPen(self.normal_pen)
        
    def updatePosition(self):
        if self.start_pin:
            start = self.start_pin.scenePos()
            if self.end_pin:
                end = self.end_pin.scenePos()
            else:
                end = self.line().p2()
            self.setLine(start.x(), start.y(), end.x(), end.y())
            
    def setEndPoint(self, point):
        if self.start_pin:
            start = self.start_pin.scenePos()
            self.setLine(start.x(), start.y(), point.x(), point.y())
    
    def removeFromPins(self):
        """Remove this wire from its connected pins"""
        if self.start_pin and self in self.start_pin.wires:
            self.start_pin.wires.remove(self)
        if self.end_pin and self in self.end_pin.wires:
            self.end_pin.wires.remove(self)

class EditableLabel(QGraphicsTextItem):
    """Custom text item that handles Enter key"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.component = parent
        
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.component:
                self.component.finishEditing()
        else:
            super().keyPressEvent(event)

class Component(QGraphicsRectItem):
    """Simple component with one input and one output"""
    def __init__(self, x, y, name=""):
        super().__init__(0, 0, 60, 40)
        self.setPos(x, y)
        self.normal_brush = QBrush(QColor(100, 150, 255))
        self.hover_brush = QBrush(QColor(150, 200, 255))
        self.setBrush(self.normal_brush)
        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Add label text at the top inside the component
        self.label = EditableLabel(name, self)
        self.label.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.label.setFont(font)
        # Center the text at the top
        text_width = self.label.boundingRect().width()
        self.label.setPos((60 - text_width) / 2, 2)
        self.label.setTextInteractionFlags(Qt.NoTextInteraction)
        
        # Input pin on the left
        self.input_pin = ConnectionPin(0, 20, self)
        # Output pin on the right
        self.output_pin = ConnectionPin(60, 20, self)
    
    def hoverEnterEvent(self, event):
        self.setBrush(self.hover_brush)
        
    def hoverLeaveEvent(self, event):
        self.setBrush(self.normal_brush)
    
    def mouseDoubleClickEvent(self, event):
        """Double-click to enable editing"""
        if event.button() == Qt.LeftButton:
            self.startEditing()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
    
    def startEditing(self):
        """Enable text editing mode"""
        self.label.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.label.setFocus()
        # Select all text
        cursor = self.label.textCursor()
        cursor.select(cursor.Document)
        self.label.setTextCursor(cursor)
        
        # Store original name for validation
        self.original_name = self.label.toPlainText()
        
        # Connect to focus out event
        self.label.document().contentsChanged.connect(self.updateLabelPosition)
    
    def eventFilter(self, obj, event):
        """Filter events to catch Enter key"""
        if obj == self.label and event.type() == event.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.finishEditing()
                return True
        return super().eventFilter(obj, event)
    
    def updateLabelPosition(self):
        """Re-center the label when text changes"""
        text_width = self.label.boundingRect().width()
        self.label.setPos((60 - text_width) / 2, 2)
    
    def focusOutEvent(self, event):
        """Validate name when losing focus"""
        if self.label.textInteractionFlags() == Qt.TextEditorInteraction:
            self.finishEditing()
        super().focusOutEvent(event)
    
    def finishEditing(self):
        """Finish editing and validate the name"""
        from PyQt5.QtWidgets import QMessageBox
        
        new_name = self.label.toPlainText().strip()
        
        # Disconnect the signal
        try:
            self.label.document().contentsChanged.disconnect(self.updateLabelPosition)
        except:
            pass
        
        # Validate the name
        if not new_name:
            QMessageBox.warning(None, 'Invalid Name', 'Component name cannot be empty!')
            self.label.setPlainText(self.original_name)
        else:
            # Check for duplicates
            name_exists = False
            if self.scene():
                for item in self.scene().items():
                    if isinstance(item, Component) and item != self and item.label.toPlainText() == new_name:
                        name_exists = True
                        break
            
            if name_exists:
                QMessageBox.warning(None, 'Duplicate Name', f'A component named "{new_name}" already exists!')
                self.label.setPlainText(self.original_name)
            else:
                self.label.setPlainText(new_name)
        
        # Disable editing
        self.label.setTextInteractionFlags(Qt.NoTextInteraction)
        self.updateLabelPosition()
        
        # Clear focus
        self.label.clearFocus()
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for wire in self.input_pin.wires + self.output_pin.wires:
                wire.updatePosition()
        return super().itemChange(change, value)
    
    def removeFromScene(self):
        """Remove this component and all connected wires"""
        # Remove all connected wires
        for wire in self.input_pin.wires[:]:
            wire.removeFromPins()
            if wire.scene():
                wire.scene().removeItem(wire)
        for wire in self.output_pin.wires[:]:
            wire.removeFromPins()
            if wire.scene():
                wire.scene().removeItem(wire)

class CircuitScene(QGraphicsScene):
    """Custom scene that handles wire drawing"""
    def __init__(self):
        super().__init__()
        self.current_wire = None
        self.drawing_wire = False
        self.panning = False
        self.last_pan_pos = None
        self.dragging_new_component = False
        self.new_component = None
        
    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        
        # If we clicked on a child item (like label or pin), get the parent component
        if isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), Component):
            component_item = item.parentItem()
        elif isinstance(item, Component):
            component_item = item
        else:
            component_item = None
        
        if event.button() == Qt.MiddleButton:
            # Start panning with middle click
            self.panning = True
            self.last_pan_pos = event.screenPos()
            event.accept()
        elif event.button() == Qt.RightButton:
            # Check what we're right-clicking on
            if component_item and not isinstance(item, ConnectionPin):
                # Delete component (but not if clicking on a pin)
                component_item.removeFromScene()
                self.removeItem(component_item)
                event.accept()
            elif isinstance(item, Wire):
                # Delete wire
                item.removeFromPins()
                self.removeItem(item)
                event.accept()
            else:
                event.accept()
        elif isinstance(item, ConnectionPin):
            # Start drawing wire with either left or right click on a pin
            self.drawing_wire = True
            self.current_wire = Wire(item, start_pos=event.scenePos())
            self.addItem(self.current_wire)
            event.accept()
        elif event.button() == Qt.LeftButton:
            # Only allow selection/dragging with left click on components
            super().mousePressEvent(event)
        else:
            # Ignore other clicks to prevent selection box
            event.accept()
            
    def mouseMoveEvent(self, event):
        if self.dragging_new_component and self.new_component:
            # Update position of new component being dragged
            self.new_component.setPos(event.scenePos().x() - 30, event.scenePos().y() - 20)
        elif self.panning and self.last_pan_pos:
            # Pan the view
            delta = event.screenPos() - self.last_pan_pos
            self.last_pan_pos = event.screenPos()
            view = self.views()[0]
            view.horizontalScrollBar().setValue(view.horizontalScrollBar().value() - delta.x())
            view.verticalScrollBar().setValue(view.verticalScrollBar().value() - delta.y())
        elif self.drawing_wire and self.current_wire:
            self.current_wire.setEndPoint(event.scenePos())
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if self.dragging_new_component:
            # Finish dragging new component
            self.dragging_new_component = False
            self.new_component = None
            event.accept()
        elif event.button() == Qt.MiddleButton and self.panning:
            # Stop panning
            self.panning = False
            self.last_pan_pos = None
            event.accept()
        elif self.drawing_wire:
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, ConnectionPin) and item != self.current_wire.start_pin:
                self.current_wire.end_pin = item
                item.wires.append(self.current_wire)
                self.current_wire.updatePosition()
            else:
                self.removeItem(self.current_wire)
            
            self.current_wire = None
            self.drawing_wire = False
        else:
            super().mouseReleaseEvent(event)

class CircuitDesigner(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circuit Designer")
        self.setGeometry(100, 100, 1000, 700)
        
        self.scene = CircuitScene()
        self.scene.setSceneRect(0, 0, 2000, 2000)
        
        self.view = CircuitView(self.scene)
        
        # Toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Component")
        add_btn.pressed.connect(self.startDraggingComponent)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clearAll)
        
        toolbar_layout.addWidget(add_btn)
        toolbar_layout.addWidget(clear_btn)
        toolbar_layout.addStretch()
        toolbar.setLayout(toolbar_layout)
        
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(toolbar)
        main_layout.addWidget(self.view)
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
        self.component_count = 0
        
    def startDraggingComponent(self):
        """Start dragging a new component from the toolbar"""
        while True:
            # Ask for component name
            name, ok = QInputDialog.getText(self, 'Component Name', 'Enter component name:')
            if not ok:
                # User cancelled
                return
            
            # Check if name is empty
            if not name.strip():
                QMessageBox.warning(self, 'Invalid Name', 'Component name cannot be empty!')
                continue
            
            # Check if name already exists
            name_exists = False
            for item in self.scene.items():
                if isinstance(item, Component) and item.label.toPlainText() == name:
                    name_exists = True
                    break
            
            if name_exists:
                QMessageBox.warning(self, 'Duplicate Name', f'A component named "{name}" already exists!\nPlease choose a different name.')
                continue
            
            # Name is valid, create component
            self.scene.dragging_new_component = True
            self.scene.new_component = Component(0, 0, name)
            self.scene.addItem(self.scene.new_component)
            break
        
    def addComponent(self):
        x = 100 + (self.component_count % 5) * 100
        y = 100 + (self.component_count // 5) * 100
        component = Component(x, y, "")
        self.scene.addItem(component)
        self.component_count += 1
        
    def clearAll(self):
        self.scene.clear()
        self.component_count = 0

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircuitDesigner()
    window.show()
    sys.exit(app.exec_())