from PyQt6.QtCore import Qt, QModelIndex
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


        self.setStyleSheet(
            """
             QHeaderView::section
            {
                    height: 14px;
                    font-size: 14px;
                    font-family: Roboto;
                    font-style: bold;
                    padding: 0px 0px 5px 5px;
                    margin: 0px;
            }
            """
        )
        # self.header().hide()
        # self.expandAll()

    def resize_listener(self, event):
        self.resize_columns()

    def resize_columns(self,multi_col_list=True):
        half_width = int(self.width()/ 2)
        # if len(self.labels) > 1:
        if multi_col_list and self.columnWidth(0) > half_width:
            self.setColumnWidth(0, half_width)
            # self.setColumnWidth(1, half_width)

    def add_folder_with_items(self, folder_name, items):
        # Create a folder item (top-level item)
        folder_item = QStandardItem(folder_name)
        folder_item.setEditable(False)  # Make the folder name non-editable
        folder_item.setSelectable(False)  # Optional: make the folder itself non-selectable
        folder_item.setToolTip("")
        folder_item.setData(None, Qt.ItemDataRole.ToolTipRole)

        # Add items to the folder
        for item_name in items:
            item = QStandardItem(item_name)
            item.setEditable(False)  # Make the item name non-editable
            item.setToolTip("")
            item.setData(None, Qt.ItemDataRole.ToolTipRole)
            folder_item.appendRow(item)

        # Add the folder to the model
        self.model.appendRow(folder_item)

    def clear(self):
        self.model.clear()

    def addItem(self,folder_item):
        self.model.appendRow(folder_item)

    def event(self, event):
        if event.type() == event.Type.ToolTip:
            return False  # Ignore tooltip events
        return super().event(event)

    def toggle_expand_state_of_item_at_row(self, table_coord: QModelIndex):
        if self.isExpanded(table_coord):
            self.collapse(table_coord)
            return False

        self.expand(table_coord)
        return True