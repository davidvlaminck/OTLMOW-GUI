from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsItem, \
    QGraphicsRectItem
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPen, QColor
import pyqtgraph as pg
import sys

class DraggableClassItem(QGraphicsRectItem):
    def __init__(self, class_name, x, y):
        super().__init__(x - 1.5, y - 1, 3, 2)  # Create a rectangle centered at (x, y)
        self.class_name = class_name
        self.setPen(QPen(QColor(100, 100, 250), 2))

        # Add a label to display the class name
        self.label = pg.TextItem(text=class_name, color=(255, 255, 255))
        self.label.setPos(x, y)

        # Set this item as movable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def mouseMoveEvent(self, event):
        # Update position of the label when the item is dragged
        super().mouseMoveEvent(event)
        self.label.setPos(self.pos().x() + 1.5, self.pos().y() + 1)

    def get_position(self):
        return self.pos().x() + 1.5, self.pos().y() + 1

class UMLClassDiagram(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Draggable UML Class Diagram with PyQtGraph")
        self.setGeometry(300, 300, 800, 600)

        # Create the PyQtGraph graphics layout widget
        self.graph_widget = pg.GraphicsLayoutWidget()
        self.plot = self.graph_widget.addPlot()
        self.plot.hideAxis('bottom')
        self.plot.hideAxis('left')

        # Define classes and relationships
        self.classes = {
            "Animal": (0, 0),
            "Mammal": (-5, -5),
            "Bird": (5, -5),
            "Dog": (-5, -10),
            "Cat": (-8, -10),
            "Sparrow": (5, -10),
            "Eagle": (8, -10)
        }
        self.relationships = [
            ("Animal", "Mammal"),
            ("Animal", "Bird"),
            ("Mammal", "Dog"),
            ("Mammal", "Cat"),
            ("Bird", "Sparrow"),
            ("Bird", "Eagle")
        ]

        # Draw the classes and relationships
        self.class_items = {}
        self.draw_classes()
        self.draw_relationships()

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.graph_widget)

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def draw_classes(self):
        for class_name, position in self.classes.items():
            x, y = position
            class_item = DraggableClassItem(class_name, x, y)
            self.plot.addItem(class_item)
            self.plot.addItem(class_item.label)
            self.class_items[class_name] = class_item

    def draw_relationships(self):
        self.relationship_lines = []
        for parent, child in self.relationships:
            parent_item = self.class_items[parent]
            child_item = self.class_items[child]

            # Draw the initial line between the parent and child classes
            line = pg.PlotDataItem(
                x=[parent_item.get_position()[0], child_item.get_position()[0]],
                y=[parent_item.get_position()[1], child_item.get_position()[1]],
                pen=pg.mkPen(color=(150, 150, 150), width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
            )
            self.plot.addItem(line)
            self.relationship_lines.append((line, parent_item, child_item))

        # Continuously update relationships when classes are moved
        self.plot.scene().sigMouseMoved.connect(self.update_relationships)

    def update_relationships(self, pos):
        # Update the position of each relationship line based on current class positions
        for line, parent_item, child_item in self.relationship_lines:
            parent_pos = parent_item.get_position()
            child_pos = child_item.get_position()

            # Update the data of the line item to match the new positions
            line.setData(
                x=[parent_pos[0], child_pos[0]],
                y=[parent_pos[1], child_pos[1]]
            )

def main():
    app = QApplication(sys.argv)
    window = UMLClassDiagram()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()