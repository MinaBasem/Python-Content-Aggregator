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
        self.setWindowTitle("Your Daily Data")
        self.setFixedSize(1200, 700)

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

        self.load_weather_ui(content_layout)    # Call the separate function to create labels and buttons
        self.load_news_ui(content_layout)
        self.load_forex_ui(content_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)
        self.show()

## Functions for displaying each kind of scraped content

    def load_weather_ui(self, layout):
        # obtain weather variables from api_server.py
        try:
            from api_server import current_temp, current_feels_like_temp, current_rain_global, daily_temperature_max, daily_temperature_min
            import api_server
            #api_server.fetch_weather_api()
        except ImportError:
            print("Error: api_server.py not found.")
            return
        
        weather_label = QLabel("Weather")
        weather_label.setAlignment(Qt.AlignCenter)
        font = weather_label.font()
        font.setPointSize(16)
        font.setBold(True)
        weather_label.setFont(font)
        layout.addWidget(weather_label)

        # Use the imported variables here
        api_server.fetch_weather_api()
        label = QLabel(f"Current Temperature: {current_temp}°C")
        layout.addWidget(label)
        label = QLabel(f"Feels Like: {current_feels_like_temp}°C")
        layout.addWidget(label)
        label = QLabel(f"Rain: {current_rain_global} mm")
        layout.addWidget(label)
        label = QLabel(f"Daily Max Temp: {daily_temperature_max}°C")
        layout.addWidget(label)
        label = QLabel(f"Daily Min Temp: {daily_temperature_min}°C")
        layout.addWidget(label)
        separator = QFrame(frameShape=QFrame.HLine)
        layout.addWidget(separator)

    def load_news_ui(self, layout):
        # obtain weather variables from api_server.py
        try:
            from api_server import headlines, source_name, headline_description, headline_url
            import api_server
        except ImportError:
            print("Error: api_server.py not found.")
            return

        news_label = QLabel("Headlines")
        news_label.setAlignment(Qt.AlignCenter)
        font = news_label.font()
        font.setPointSize(16)
        font.setBold(True)
        news_label.setFont(font)
        layout.addWidget(news_label)

        api_server.fetch_news_api()
        for index in range(5):
            label = QLabel(f"Headline: {headlines[index]}")
            layout.addWidget(label)
            label = QLabel(f"Source: {source_name[index]}")
            layout.addWidget(label)
            label = QLabel(f"Description: {headline_description[index]}")
            layout.addWidget(label)
            label = QLabel(f"Link: {headline_url[index]}")
            layout.addWidget(label)
            separator = QFrame(frameShape=QFrame.HLine)
            layout.addWidget(separator)

    def load_forex_ui(self, layout):
        try:
            from api_server import currencies, currency_pairs, currency_pairs_values
            import api_server
        except ImportError:
            print("Error: api_server.py not found.")
            return
        
        forex_label = QLabel("Forex")
        forex_label.setAlignment(Qt.AlignCenter)
        font = forex_label.font()
        font.setPointSize(16)
        font.setBold(True)
        forex_label.setFont(font)
        layout.addWidget(forex_label)

        api_server.fetch_forex_api()
        horizontal_layout = QHBoxLayout()

        for currency in range(5):
            #label = QLabel(f"Pair: {currencies[currency]}")
            vertical_layout = QVBoxLayout()
            label = QLabel("Pair: 30")
            vertical_layout.addWidget(label)
            #label = QLabel(f"Value: {currency_pairs_values[currency]}")
            label = QLabel("Value: 50")
            vertical_layout.addWidget(label)
            horizontal_layout.addLayout(vertical_layout)

        separator = QFrame(frameShape=QFrame.HLine)
        layout.addWidget(separator)
        layout.addLayout(horizontal_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
