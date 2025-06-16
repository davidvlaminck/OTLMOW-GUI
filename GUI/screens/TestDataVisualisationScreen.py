import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl

from GUI.screens.Screen import Screen


class Backend(QObject):
    @pyqtSlot(str)
    def receiveMessage(self, msg):
        print(f"Message from JS: {msg}")

class TestDataVisualisationScreen(Screen):
    def reset_ui(self, _):
        pass

    def __init__(self):
        super().__init__()
        # self.setWindowTitle("PyQt6 QWebEngine QWebChannel Example")
        # self.resize(800, 600)

        # Set up QWebEngineView
        self.view = QWebEngineView(self)
        # self.setCentralWidget(self.view)

        # Set up the channel and backend
        self.channel = QWebChannel()
        self.backend = Backend()
        self.channel.registerObject("backend", self.backend)
        self.view.page().setWebChannel(self.channel)

        # Load HTML
        html = r"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        window.backend = channel.objects.backend;
                        alert("create webchannel")
                        document.body.addEventListener("click", function(event) {
                            const msg = `Clicked at (${event.clientX}, ${event.clientY})`;
                            backend.receiveMessage(msg);
                        });
                    });
                });
            </script>
            <style>
                body { font-family: sans-serif; text-align: center; margin-top: 50px; }
            </style>
        </head>
        <body>
            <h1>Click anywhere to send data to Python</h1>
            <p>Open your Python console to see the coordinates.</p>
        </body>
        </html>
        """

        self.view.setHtml(html, QUrl("qrc:///"))

        self.container_insert_data_screen = QVBoxLayout()
        self.container_insert_data_screen.addWidget(self.view)

        self.setLayout(self.container_insert_data_screen)
