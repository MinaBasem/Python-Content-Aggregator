from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.web_view = QWebEngineView(self)
        html_content = """
        <html><body>
            <h1>Hello, PyQt5!</h1>
        </body></html>"""
        self.web_view.setHtml(html_content)
        self.setCentralWidget(self.web_view)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()