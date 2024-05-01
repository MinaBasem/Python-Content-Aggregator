import pandas as pd
import time
from socket import *
import os
import re
import requests
from html.parser import HTMLParser
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

class MyParser(HTMLParser):
    def handle_data(self, data):
        self.data += data

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
        self.search_button.clicked.connect(self.search)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_box)
        top_layout.addWidget(self.search_button)

        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setAlignment(Qt.AlignTop)

        for i in range(5):
            label = QLabel(f"Label {i + 1}")
            button = QPushButton(f"Button {i + 1}")
            content_layout.addWidget(label)
            content_layout.addWidget(button)

            # Add a horizontal separator line after each pair
            separator = QFrame(frameShape=QFrame.HLine)
            content_layout.addWidget(separator)

        #self.layout.addWidget(self.scroll_area)

        self.scroll_area = QScrollArea()
        #self.scroll_area.setStyleSheet("background-color: White;")
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)
        self.show()


## Create functions for displaying each kind of scraped content
## Functions below

    def search(self):
        search_query = self.search_box.text()
        HOST = "google.com"
        PORT = 80

        clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            clientSocket.connect((HOST, PORT))

            # HTTP request (GET method, search path, and headers)
            search_query = str(search_query.replace(" ", "+"))
            request = f"GET /search?q={search_query}&collection=default_collection&frontend=default_frontend HTTP/1.1\r\nHost: www.google.com\r\nConnection: close\r\n\r\n"
            clientSocket.sendall(request.encode())  # Send request encoded in bytes

            # Receive response (accumulate data in chunks)
            received_data = b''
            while True:
                # Receive data in chunks (adjust buffer size as needed)
                data = clientSocket.recv(100000)
                if not data:  # Check if data reception is complete
                    break
                received_data += data

            # Decode and print the entire response
            decoded_response = received_data.decode('latin-1')
            parser = MyParser()
            parser.data = ''
            parser.feed(decoded_response)

            with open("received_page.html", "w") as f:
                f.write(decoded_response)
                #print(decoded_response)
                self.extract_links()


        finally:
            # Close the socket connection (ensure execution even on errors)
            clientSocket.close()

    def extract_links(self):
        links = []
        try:
            with open("received_page.html", "r") as f:
                html_content = f.read()

            links = re.findall(r'<a.*?href="(.*?)"', html_content)
            #links = [link for link in links if "https" in link.lower()]

            with open("links.txt", "w") as f:
                for link in links:
                    #link = link.split('/url?q=')[1]
                    f.write(link + "\n")
                print("Done extracting links")

        except FileNotFoundError:
            print("Error: File 'received_page.html' not found.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())