from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsRectItem, \
    QGraphicsItem, QGraphicsEllipseItem
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPen, QColor
import pyqtgraph as pg
import sys


class DraggableClassItem(QGraphicsRectItem):
    def __init__(self, class_name, x, y):
        super().__init__(x - 1.5, y - 1, 3, 2)
        self.class_name = class_name
        self.setPen(QPen(QColor(100, 100, 250), 2))

        self.label = pg.TextItem(text=class_name, color=(255, 255, 255))
        self.label.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.label.setPos(self.pos().x() + 1.5, self.pos().y() + 1)

    def get_position(self):
        return self.pos().x() + 1.5, self.pos().y() + 1


class DraggableJointItem(QGraphicsEllipseItem):
    def __init__(self, x, y):
        super().__init__(x - 0.5, y - 0.5, 1, 1)  # Create a small circle centered at (x, y)
        self.setBrush(QColor(200, 50, 50))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def get_position(self):
        return self.pos().x() + 0.5, self.pos().y() + 0.5


class UMLClassDiagram(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Draggable UML Class Diagram with Joints")
        self.setGeometry(300, 300, 800, 600)

        self.graph_widget = pg.GraphicsLayoutWidget()
        self.plot = self.graph_widget.addPlot()
        self.plot.hideAxis('bottom')
        self.plot.hideAxis('left')

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

        # Draw classes and relationships with joints
        self.class_items = {}
        self.draw_classes()
        self.draw_relationships()

        layout = QVBoxLayout()
        layout.addWidget(self.graph_widget)

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

            # Create initial joint position as the midpoint
            parent_pos = parent_item.get_position()
            child_pos = child_item.get_position()
            joint_x = (parent_pos[0] + child_pos[0]) / 2
            joint_y = (parent_pos[1] + child_pos[1]) / 2
            joint_item = DraggableJointItem(joint_x, joint_y)

            # Draw the line with the joint as an intermediate point
            line = pg.PlotDataItem(
                x=[parent_pos[0], joint_x, child_pos[0]],
                y=[parent_pos[1], joint_y, child_pos[1]],
                pen=pg.mkPen(color=(150, 150, 150), width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
            )
            self.plot.addItem(line)
            self.plot.addItem(joint_item)

            # Track each line and its components (parent, child, joint)
            self.relationship_lines.append((line, parent_item, child_item, joint_item))

        # Update lines when items are moved
        self.plot.scene().sigMouseMoved.connect(self.update_relationships)

    def update_relationships(self, pos):
        for line, parent_item, child_item, joint_item in self.relationship_lines:
            parent_pos = parent_item.get_position()
            child_pos = child_item.get_position()
            joint_pos = joint_item.get_position()

            # Update the data of the line with new positions including the joint
            line.setData(
                x=[parent_pos[0], joint_pos[0], child_pos[0]],
                y=[parent_pos[1], joint_pos[1], child_pos[1]]
            )


def main():
    app = QApplication(sys.argv)
    window = UMLClassDiagram()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
