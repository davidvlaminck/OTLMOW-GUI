from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, \
    QWidget
from PyQt6.QtCore import QDir
import sys


class FileSystemViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("QFileSystemModel Example")
        self.setGeometry(300, 300, 800, 600)

        # Create the QFileSystemModel
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())  # Set root path to the filesystem root

        # Create a QTreeView to display the filesystem
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)

        # Set the root index to a specific directory (e.g., the user's home directory)
        home_directory = QDir.homePath()
        self.tree_view.setRootIndex(self.model.index(home_directory))

        # Optional: Hide columns other than the file name
        self.tree_view.setColumnHidden(1, True)  # Size column
        self.tree_view.setColumnHidden(2, True)  # Type column
        self.tree_view.setColumnHidden(3, True)  # Date Modified column

        # Set up the layout and central widget
        layout = QVBoxLayout()
        layout.addWidget(self.tree_view)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


def main():
    app = QApplication(sys.argv)
    window = FileSystemViewer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()