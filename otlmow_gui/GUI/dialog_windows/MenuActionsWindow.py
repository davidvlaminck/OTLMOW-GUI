from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QFrame, QHBoxLayout

from otlmow_gui.Domain.network.Updater import Updater


class MenuActionsWindow:

    def __init__(self, language):
        self._ = language

    def create_about_window(self):
        window = QDialog()
        window_layout = QVBoxLayout()
        window.setMinimumWidth(500)
        window.setWindowTitle(self._('about'))
        version_box = self.version_box()
        window_layout.addWidget(version_box)
        mady_by_title = QLabel(self._('made_by') + ':')
        window_layout.addWidget(mady_by_title)
        window_layout.addWidget(self.creator_box('Jasper Berton', 'jasperberton1@telenet.be'))
        window_layout.addWidget(self.creator_box('David Vlaminck', 'david.vlaminck@mow.vlaanderen.be'))
        window_layout.addWidget(self.creator_box('Bert Van Overmeir','bert.vanovermeir@mow.vlaanderen.be'))
        window_layout.addWidget(
            self.creator_box('Christiaan Vanbergen', 'christiaan.vanbergen.btf@gmail.com'))
        window.setLayout(window_layout)
        window.exec()

    def create_error_report_window(self):
        window = QDialog()
        window_layout = QVBoxLayout()
        window.setMinimumWidth(500)
        window.setWindowTitle(self._('error_title'))
        error_title = QLabel(self._('error_report'))
        contact = QLabel(self._('contact') + ':')
        window_layout.addWidget(error_title)
        window_layout.addWidget(contact)
        window_layout.addWidget(self.creator_box('team BIM', 'TeamBim@verzendlijst.wegenenverkeer.be'))
        window.setLayout(window_layout)
        window.exec()

    def version_box(self):
        version_box = QFrame()
        version_box_layout = QHBoxLayout()
        version = Updater.get_project_version()

        version_title = QLabel(self._('version') + ':')
        version_number = QLabel(f'{version}')
        version_box_layout.addWidget(version_title)
        version_box_layout.addWidget(version_number)
        version_box.setLayout(version_box_layout)
        return version_box

    @classmethod
    def creator_box(cls, name, mail):
        creator_box = QFrame()
        creator_box_layout = QHBoxLayout()
        creator_name = QLabel(name)
        creator_box_layout.addWidget(creator_name)
        creator_mail = QLabel(f"<a href='mailto:{mail}'>{mail}</a>")
        creator_mail.setOpenExternalLinks(True)
        creator_box_layout.addWidget(creator_mail)
        creator_box.setLayout(creator_box_layout)
        return creator_box

