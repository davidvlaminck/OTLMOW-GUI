from pathlib import Path

from PyQt6.QtWidgets import QTabWidget, QVBoxLayout

from otlmow_gui.Domain import global_vars
from otlmow_gui.GUI.dialog_windows.YesOrNoNotificationWindow import YesOrNoNotificationWindow
from otlmow_gui.GUI.screens.Screen import Screen
from otlmow_gui.GUI.header.HeaderBar import HeaderBar
from otlmow_gui.GUI.header.StepperWidget import StepperWidget

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent / 'locale/'


class TabWidget(Screen):

    def __init__(self, language, page_nr: int, widget1, description1: str, has_save_btn: bool = True, **kwargs):
        super().__init__()
        self._ = language
        self.tabs = QTabWidget()
        self.tab1 = widget1
        self.desc1 = description1
        self.stepper_widget = StepperWidget(self._, page_nr)
        self.header = HeaderBar(language=self._, has_save_btn=has_save_btn)
        self.main_window = None
        self.create_tab(widget1, **kwargs)
        self.layout = QVBoxLayout(self)
        self.fill_up_layout()

        self.init_ui()

    def create_tab(self, main_widget, **kwargs):
        self.tabs.addTab(main_widget, self._(self.desc1))
        widget2 = kwargs.get('widget2', None)
        widget3 = kwargs.get('widget3', None)
        if widget2 is not None:
            self.tab2 = widget2
            self.desc2 = kwargs.get('description2', None)
            self.tabs.addTab(self.tab2, self._(self.desc2))
            self.tabs.currentChanged.connect(self.tab2.opened)
        if widget3 is not None:
            self.tab3 = widget3
            self.desc3 = kwargs.get('description3', None)
            self.tabs.addTab(self.tab3, self._(self.desc3))

    def fill_up_layout(self):
        self.layout.addWidget(self.header)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.stepper_widget.stepper_widget())
        self.layout.addSpacing(10)
        self.layout.addWidget(self.tabs)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.tabs.setProperty('class', 'tab-widget')

    def onClickReturnToHomeScreen(self):

        # first check if there are any unsaved changes in the graph
        if (global_vars.current_project and
            not global_vars.current_project.get_saved_graph_status()):

            title = self._("unsaved_graph_changes_warning_title")
            text = self._("unsaved_graph_changes_warning_text")
            alt_yes_text = self._("Continue")
            alt_no_text = self._("Back")

            warning_dialog = YesOrNoNotificationWindow(message=text,
                                                       title=title,
                                                       alt_yes_text=alt_yes_text,
                                                       alt_no_text=alt_no_text)
            answer = warning_dialog.exec()

            if answer == 16384:  # QMessageBox.ButtonRole.YesRole:
                # close project without doing anything else
                pass
            elif answer == 65536: # QMessageBox.ButtonRole.NoRole:
                # don't close project return to project
                return
            elif answer == 262144: # QMessageBox.ButtonRole.AbortRole also X-button
                # don't close project return to project
                return


        self.main_window.setCurrentIndex(0)
        global_vars.current_project.clear_model_builder_from_memory()
        global_vars.current_project = None
        self.main_window.home_screen.sort_on_last_edit()

    def init_ui(self):
        returnToHomeScreenButton = self.header.header_bar_detail_screen()
        returnToHomeScreenButton.clicked.connect(self.onClickReturnToHomeScreen)

    def reset_ui(self, _):
        super().reset_ui(_)
        self._ = _
        # OTLLogger.logger.debug("resetting a tab widget")
        self.header.reset_ui(_)
        if hasattr(self, 'tab2'):
            self.tab2.reset_ui(_)
            self.tabs.setTabText(1, self._(self.desc2))
        if hasattr(self, 'tab3'):
            self.tab3.reset_ui(_)
            self.tabs.setTabText(2, self._(self.desc3))
        # self.tab1.reset_ui(_)
        self.tabs.setTabText(0, self._(self.desc1))
        self.stepper_widget.reset_ui(_)
