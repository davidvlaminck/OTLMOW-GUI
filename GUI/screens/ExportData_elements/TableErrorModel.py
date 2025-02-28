from typing import Any

from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex


class TableErrorModel(QAbstractTableModel):
    def __init__(self, data, language_settings):
        super(TableErrorModel, self).__init__()
        self._data = data
        self._ = language_settings
        self.header_labels = [self._('error')]

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        if self._data and self._data[0]:
            return len(self._data[0])
        else:
            return 0

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
