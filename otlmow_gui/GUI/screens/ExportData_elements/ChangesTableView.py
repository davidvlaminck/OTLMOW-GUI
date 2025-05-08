from PyQt6.QtWidgets import QTableView, QHeaderView


class ChangesTableView(QTableView):

    def __init__(self):
        super().__init__()
        self.did_first_paint = False
        self.did_second_paint = False

    def paintEvent(self, e):
        super().paintEvent(e)

        if not self.did_first_paint:
            self.did_first_paint = True
        elif not self.did_second_paint:
            self.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive)
            self.did_second_paint = True


    def resetPainting(self):
        self.did_first_paint = False
        self.did_second_paint = False
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)

    def setModel(self, model):
        self.resetPainting()
        super().setModel(model)


