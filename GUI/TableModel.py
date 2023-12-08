from PyQt6.QtCore import QAbstractTableModel, Qt


class TableModel(QAbstractTableModel):

    def __init__(self, data, language_settings):
        super(TableModel, self).__init__()
        self._data = data
        self._ = language_settings
        self.header_labels = [self._('id'), self._('action'), self._("name_attribute"), self._("old_attribute"),
                              self._("new_attribute")]

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
