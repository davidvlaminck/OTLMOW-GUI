from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import sys

class CustomTreeView(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Custom QStandardItemModel Example")
        self.setGeometry(300, 300, 400, 300)

        # Create the QStandardItemModel
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Folders and Items"])

        # Add custom folders and items
        self.add_folder_with_items("Folder 1", ["Item 1.1", "Item 1.2", "Item 1.3"])
        self.add_folder_with_items("Folder 2", ["Item 2.1", "Item 2.2"])
        self.add_folder_with_items("Folder 3", ["Item 3.1", "Item 3.2", "Item 3.3", "Item 3.4"])

        # Create a QTreeView and set the model
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()  # Expand all items initially

        # Set up the layout and central widget
        layout = QVBoxLayout()
        layout.addWidget(self.tree_view)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_folder_with_items(self, folder_name, items):
        # Create a folder item (top-level item)
        folder_item = QStandardItem(folder_name)
        folder_item.setEditable(False)  # Make the folder name non-editable
        folder_item.setSelectable(False)  # Optional: make the folder itself non-selectable

        # Add items to the folder
        for item_name in items:
            item = QStandardItem(item_name)
            item.setEditable(False)  # Make the item name non-editable
            folder_item.appendRow(item)

        # Add the folder to the model
        self.model.appendRow(folder_item)


def main():
    app = QApplication(sys.argv)
    window = CustomTreeView()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()