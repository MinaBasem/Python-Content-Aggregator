import pandas as pd
import time
from socket import *
import os
import sys
from PyQt5.QtCore import (Qt, QSize, QUrl)
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QLineEdit,
    QFrame,
    QListWidgetItem,
    QMessageBox,
    QScrollArea
)

## Create UI

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle("File Transfer")
        self.setFixedSize(700, 500)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_button = QPushButton("Search")
        #self.search_button.clicked.connect(self.search)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_box)
        top_layout.addWidget(self.search_button)

        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setAlignment(Qt.AlignTop)

        label_1 = QLabel("Label 1")
        label_2 = QLabel("Label 2")
        label_3 = QLabel("Label 3")
        
        button1 = QPushButton("Button 1")
        button2 = QPushButton("Button 2")
        button3 = QPushButton("Button 3")

        self.setStyleSheet("QLabel, QPushButton, QFrame { color: White; }")
        #self.setStyleSheet("QPushButton { color: White; }")

        content_layout.addWidget(label_1)
        content_layout.addWidget(button1)
        content_layout.addWidget(QFrame(frameShape=QFrame.HLine))

        content_layout.addWidget(label_2)
        content_layout.addWidget(button2)
        content_layout.addWidget(QFrame(frameShape=QFrame.HLine))

        content_layout.addWidget(label_3)
        content_layout.addWidget(button3)
        content_layout.addWidget(QFrame(frameShape=QFrame.HLine))

        #self.layout.addWidget(self.scroll_area)

        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("background-color: black;")
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)
        self.show()


## Create functions for displaying each kind of scraped content

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())