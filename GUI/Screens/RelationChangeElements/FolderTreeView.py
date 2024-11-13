from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QTreeView, QVBoxLayout


class FolderTreeView(QTreeView):
    def __init__(self):
        super().__init__()

        # Create the QStandardItemModel
        self.model = QStandardItemModel()
        # self.model.setHorizontalHeaderLabels(["Folders and Items"])

        # Add custom folders and items
        # self.add_folder_with_items("Folder 1", ["Item 1.1", "Item 1.2", "Item 1.3"])
        # self.add_folder_with_items("Folder 2", ["Item 2.1", "Item 2.2"])
        # self.add_folder_with_items("Folder 3", ["Item 3.1", "Item 3.2", "Item 3.3", "Item 3.4"])

        self.setModel(self.model)
        self.header().hide()
        # self.expandAll()

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

    def clear(self):
        self.model.clear()

    def addItem(self,folder_item):
        self.model.appendRow(folder_item)