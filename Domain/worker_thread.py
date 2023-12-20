import asyncio

from PyQt6.QtCore import QThread
from qasync import QEventLoop


class WorkerThread(QThread):

    def run(self):
        loop = QEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_forever()
