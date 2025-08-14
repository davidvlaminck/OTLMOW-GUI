from datetime import datetime

from PyQt6.QtWidgets import QTableWidgetItem


class OverviewTableItem(QTableWidgetItem):
    
    date_format: str = "%d-%m-%Y"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __lt__(self, other):
        try:
            return  datetime.strptime(self.text(), OverviewTableItem.date_format) < datetime.strptime(other.text(), OverviewTableItem.date_format)
        except ValueError:
            return super().__lt__(other)

    def __gt__(self, other):

        try:
            return datetime.strptime(self.text(), OverviewTableItem.date_format) > datetime.strptime(other.text(),
                                                                                     OverviewTableItem.date_format)
        except ValueError:
            return super().__gt__(other)

    def __le__(self, other):
        try:
            return datetime.strptime(self.text(), OverviewTableItem.date_format) < datetime.strptime(other.text(),
                                                                                     OverviewTableItem.date_format)
        except ValueError:
            return super().__le__(other)

    def __ge__(self, other):

        try:
            return datetime.strptime(self.text(), OverviewTableItem.date_format) > datetime.strptime(other.text(),
                                                                                     OverviewTableItem.date_format)
        except ValueError:
            return super().__ge__(other)
