from PyQt6.QtWidgets import QTableView, QHeaderView


class ChangesTableView(QTableView):

    def __init__(self):
        super().__init__()
        self.did_first_paint = False
        self.did_second_paint = False
        self.previous_width = 0

    def paintEvent(self, e):
        super().paintEvent(e)

        curr_frame_width = self.frameRect().width()
        if not self.previous_width:
            self.previous_width = curr_frame_width
        elif curr_frame_width != self.previous_width:
            self.resetPainting()
            self.previous_width = curr_frame_width

        if not self.did_first_paint:
            self.did_first_paint = True
        elif not self.did_second_paint:
            hor_headers = self.horizontalHeader()
            hor_headers.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            if hor_headers.count():
                self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            self.did_second_paint = True


    def resetPainting(self):
        self.did_first_paint = False
        self.did_second_paint = False
        hor_headers = self.horizontalHeader()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        if hor_headers.count():
            self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

    def setModel(self, model):
        super().setModel(model)
        self.resetPainting()


