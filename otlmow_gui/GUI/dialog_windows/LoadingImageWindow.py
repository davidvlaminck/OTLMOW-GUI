import asyncio
import datetime
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont, QMovie
from PyQt6.QtCore import Qt, QSize

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception

ROOT_DIR = Path(__file__).parent.parent.parent


def add_loading_screen(func):
    """Decorator that saves assets after executing the decorated function.

    This decorator wraps a function to ensure that after its execution, the current
    project's assets in memory are updated and saved. It also starts the event loop
    for the header in the main window to animate the OTL Wizard 2 logo during saving.

    :param func: The function to be decorated.
    :returns: The wrapper function that includes the saving logic.
    """

    async def wrapper_func(*args, **kwargs):
        if global_vars.test_mode:
            res = await func(*args, **kwargs)
            return res

        LoadingImageWindow.attempt_show_loading_screen(func.__name__)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        res = await func(*args, **kwargs)
        LoadingImageWindow.attempt_destoy_loading_screen(func.__name__)
        return res

    return wrapper_func

def add_loading_screen_no_delay(func):
    """Decorator that saves assets after executing the decorated function.

    This decorator wraps a function to ensure that after its execution, the current
    project's assets in memory are updated and saved. It also starts the event loop
    for the header in the main window to animate the OTL Wizard 2 logo during saving.

    :param delay: if there is a delay in opening the loading screen
    :param func: The function to be decorated.
    :returns: The wrapper function that includes the saving logic.
    """

    async def wrapper_func(*args, **kwargs):
        if global_vars.test_mode:
            res = await func(*args, **kwargs)
            return res

        LoadingImageWindow.attempt_show_loading_screen(func.__name__, delay=False)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        res = await func(*args, **kwargs)
        LoadingImageWindow.attempt_destoy_loading_screen(func.__name__)
        return res

    return wrapper_func


class LoadingImageWindow(QDialog):
    ref_key_to_time_dict = {}
    loading_window = None

    IMG_DIR = ProgramFileStructure.get_dynamic_library_path('img')

    image_path = IMG_DIR /  "cat_fly_animation.gif"
    # image_path = "C:\\Users\\chris\\PycharmProjects\\OTLMOW-GUI\\img\\yoda_patience.jpg"
    # image_path = "C:\\Users\\chris\\PycharmProjects\\OTLMOW-GUI\\img\\cat_fly_animation.gif"

    message = "Loading"
    title = "Loading"
    def __init__(self, parent=None, delayed_opening = False):
        super().__init__(parent)


        self.setWindowTitle(LoadingImageWindow.title)
        # self.setFixedSize(625, 468)
        self.setFixedSize(625, 350)
        self.setModal(True)  # Makes it a modal dialog
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # Remove the close button
        # self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)

        # Main layout
        layout = QVBoxLayout()

        # Image label
        image_abs_path_str = str(LoadingImageWindow.image_path.absolute())
        OTLLogger.logger.debug(f"loading_gif_path: {image_abs_path_str}")
        self.movie = QMovie(image_abs_path_str)
        self.movie.setScaledSize(QSize(625,468).scaled(int(625*1.5),int(468*1.5),Qt.AspectRatioMode.KeepAspectRatioByExpanding))

        movie_label = QLabel(self)
        movie_label.setMovie(self.movie)
        movie_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Text label
        text_label = QLabel(LoadingImageWindow.message, self)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)

        font = QFont()
        font.setPointSize(32)  # Adjust font size as needed
        text_label.setFont(font)



        # Add widgets to main layout
        layout.addWidget(movie_label)
        layout.addWidget(text_label)

        self.paintIntervals = []

        self.setLayout(layout)
        self.opening = True
        self.last_time = datetime.datetime.now()
        if delayed_opening:
            create_task_reraise_exception(self.delayed_open())
        else:
            self.open()
            self.movie.start()

    def paintEvent(self, *args, **kwargs):



        current_time = datetime.datetime.now()
        time_dif: datetime.timedelta = current_time - self.last_time
        self.last_time = current_time
        time_dif_seconds = time_dif.seconds + time_dif.microseconds / 1000000

        self.paintIntervals.append(time_dif_seconds)

    def closeEvent(self, event):
        # Ignore the close event to prevent closing with the 'X' button
        event.ignore()

    def close(self):
        self.opening = False

        if not self.isHidden():
            self.movie.stop()
            return super().close()


    async def delayed_open(self):
        # only open loading window after 1 second after initialisation
        # and only if the command to close it hasn't come yet by then
        OTLLogger.logger.debug("delayed open loadingscreen",
                               extra={"timing_ref": "open_loading_screen"})
        await asyncio.sleep(1)
        if self.opening:
            OTLLogger.logger.debug("still opening loadingscreen",
                                   extra={"timing_ref": "open_loading_screen"})
            self.open()
            self.movie.start()
            OTLLogger.logger.debug(f"movie scale {self.movie.scaledSize()}")
        else:
            OTLLogger.logger.debug("canceled opening loadingscreen",
                                   extra={"timing_ref": "open_loading_screen"})

    @classmethod
    def attempt_show_loading_screen(cls, ref: str,delay = True):
        # only create the loading screen if it hasn't already been created
        if not LoadingImageWindow.loading_window:
            loading_window = LoadingImageWindow(delayed_opening=delay)
            LoadingImageWindow.loading_window = {ref: loading_window}

    @classmethod
    def attempt_destoy_loading_screen(cls, ref: str):
        # only destory the loading screen in ref was the one who initiated the loading screen
        if LoadingImageWindow.loading_window:
            if ref in LoadingImageWindow.loading_window:

                current_loading_window = LoadingImageWindow.loading_window[ref]
                if current_loading_window.paintIntervals:
                    interval_count = len(current_loading_window.paintIntervals)
                    total_time = sum(current_loading_window.paintIntervals)
                    max_interval = max(current_loading_window.paintIntervals)
                    min_interval = min(current_loading_window.paintIntervals)
                    avg_interval =  total_time/interval_count
                    text = "Loading screen frame intervals: count: {interval_count}, tot: {tot:07.3f}s, max: {max:07.3f}s, min: {min:07.3f}s,avg: {avg:07.3f}s, all: [".format(interval_count=interval_count,tot=total_time,max=max_interval,min=min_interval,avg=avg_interval)
                    for time in current_loading_window .paintIntervals:
                        text += "{time:07.3f},".format(time=time)

                    text += "]"
                    OTLLogger.logger.debug(text)

                current_loading_window.close()
                LoadingImageWindow.loading_window = None
            elif ref == "crash":
                OTLLogger.logger.debug("ImageLoadingScreen closed by crash!!")
                stack = traceback.extract_stack(limit=3)
                OTLLogger.logger.debug(stack)
                current_loading_window = list(LoadingImageWindow.loading_window.values())[0]
                current_loading_window.close()
                LoadingImageWindow.loading_window = None