from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsRectItem
from pyqtgraph import GraphicsLayoutWidget, TextItem, PlotDataItem, mkPen
import pyqtgraph as pg
import sys

class UMLClassDiagram(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("UML Class Diagram with PyQtGraph")
        self.setGeometry(300, 300, 800, 600)

        # Create the PyQtGraph graphics layout widget
        self.graph_widget = GraphicsLayoutWidget()
        self.plot = self.graph_widget.addPlot()
        self.plot.hideAxis('bottom')
        self.plot.hideAxis('left')

        # Define classes and relationships
        classes = {
            "Animal": (0, 0),
            "Mammal": (-5, -5),
            "Bird": (5, -5),
            "Dog": (-5, -10),
            "Cat": (-8, -10),
            "Sparrow": (5, -10),
            "Eagle": (8, -10)
        }
        relationships = [
            ("Animal", "Mammal"),
            ("Animal", "Bird"),
            ("Mammal", "Dog"),
            ("Mammal", "Cat"),
            ("Bird", "Sparrow"),
            ("Bird", "Eagle")
        ]

        # Draw the classes and relationships
        self.draw_classes(classes)
        self.draw_relationships(classes, relationships)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.graph_widget)

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def draw_classes(self, classes):
        for class_name, position in classes.items():
            x, y = position
            # Draw a rectangle for each class
            rect = QGraphicsRectItem(x - 1.5, y - 1, 3, 2)
            rect.setPen(mkPen(color=(100, 100, 250), width=2))
            self.plot.addItem(rect)

            # Add the class name label
            label = TextItem(text=class_name, color=(255, 255, 255))
            label.setPos(x, y)
            self.plot.addItem(label)

    def draw_relationships(self, classes, relationships):
        for parent, child in relationships:
            parent_pos = classes[parent]
            child_pos = classes[child]

            # Draw a line between the parent and child classes
            line = PlotDataItem(
                x=[parent_pos[0], child_pos[0]],
                y=[parent_pos[1], child_pos[1]],
                pen=mkPen(color=(150, 150, 150), width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
            )
            self.plot.addItem(line)

def main():
    app = QApplication(sys.argv)
    window = UMLClassDiagram()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
