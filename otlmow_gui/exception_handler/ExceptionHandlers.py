import asyncio
import sys
import traceback
from typing import Awaitable

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.GUI.screens.ErrorScreen import ErrorScreen


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    OTLLogger.logger.error("error caught!")
    OTLLogger.logger.error("error message: \n: " + tb)
    error_screen = ErrorScreen(tb)
    error_screen.show()
    # QApplication.quit()


def create_task_reraise_exception(awaitable: Awaitable) -> asyncio.Task:
    async def _reraise_exception(awaitable):
        try:
            return await awaitable
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            # Call your excepthook
            excepthook(exc_type, exc_value, exc_tb)

    event_loop = asyncio.get_event_loop()
    return  event_loop.create_task(_reraise_exception(awaitable))