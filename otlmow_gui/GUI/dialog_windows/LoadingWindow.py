import asyncio

from PyQt6.QtWidgets import QMessageBox

from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class LoadingWindow(QMessageBox):



    def __init__(self, message:str = "Loading", title:str = "Loading", delayed_opening = False):
        super().__init__()
        self.message = message
        self.title = title
        self.opening = True
        self.delayed_opening = delayed_opening
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setText(self.message)
        self.setStandardButtons(QMessageBox.NoButton)
        if self.delayed_opening:
            create_task_reraise_exception(self.delayed_open())
        else:
            self.open()

    def close(self):
        self.opening = False
        return super().close()

    async def delayed_open(self):
        # only open loading window after 1 second after initialisation
        # and only if the command to close it hasn't come yet by then
        await asyncio.sleep(1)
        if self.opening:
            self.open()



