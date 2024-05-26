from PyQt6.QtCore import QEvent, QSize, Qt
from PyQt6.QtGui import QIcon, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QMainWindow,
    QToolButton,
    QWidget,
    QGraphicsDropShadowEffect,
    QScrollArea,
    QListWidget,
    QListWidgetItem
)
from socket import *
import socket
from importlib.machinery import SourceFileLoader
import os
import sys
from PyQt6.QtGui import QFont, QPixmap, QColor, QBrush
from PyQt6.QtCore import (Qt, QSize, QUrl)
from PyQt5.QtWebEngineWidgets import QWebEngineView

import api_server

currency_dict = {}

def receive_variables_file():
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 65432

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            file_data = b""
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file_data += data

            client_socket.close()

        with open("variables_received.txt", "wb") as file:
            file.write(file_data)

        with open("variables_received.txt", "rb") as file:
            file_content = file.read()

        decoded_content = file_content.decode('utf-8', errors='ignore')
        decoded_content = [line for line in decoded_content.splitlines() if line.strip()]   # To remove empty lines
        decoded_content = '\n'.join(decoded_content)

        with open("variables_received.py", "w", encoding='utf-8') as file:
            file.write(decoded_content)

    except (ConnectionRefusedError, OSError):
        print("Error: Could not connect to server. Client will display old data...")

def load_variables_from_file():
    variables_module = SourceFileLoader("variables_received", "./variables_received.py").load_module()

    for var_name in dir(variables_module):
        if not var_name.startswith("__"):
            globals()[var_name] = getattr(variables_module, var_name)

    timezone = variables_module.timezone
    current_temp = variables_module.current_temp
    trending_topics = variables_module.trending_topics
    current_feels_like_temp = variables_module.current_feels_like_temp
    headlines = variables_module.headlines
    source_name = variables_module.source_name
    headline_description = variables_module.headline_description
    headline_url = variables_module.headline_url
    currency_dict = variables_module.currency_dict
    job_titles = variables_module.job_titles
    job_company = variables_module.job_company
    job_location = variables_module.job_location


receive_variables_file()        # Receive variables first then load ui
load_variables_from_file()

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initial_pos = None
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(1, 1, 1, 1)
        title_bar_layout.setSpacing(2)
        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            """
        QLabel { text-transform: uppercase; font-size: 10pt; margin-left: 48px; }
        """
        )

        if title := parent.windowTitle():
            self.title.setText(title)
            font = self.title.font()
            font.setPointSize(16)
            font.setBold(True)
            font.setItalic(True)
            self.title.setFont(font)
            self.title.setStyleSheet("color: white;")
            self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_bar_layout.addWidget(self.title)
        # Min button
        self.min_button = QToolButton(self)
        min_icon = QIcon()
        min_icon.addFile("min.svg")
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Max button
        self.max_button = QToolButton(self)
        max_icon = QIcon()
        max_icon.addFile("max.svg")
        self.max_button.setIcon(max_icon)
        self.max_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = QToolButton(self)
        close_icon = QIcon()
        close_icon.addFile("close.svg")  # Close has only a single state.
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        # Normal button
        self.normal_button = QToolButton(self)
        normal_icon = QIcon()
        normal_icon.addFile("normal.svg")
        self.normal_button.setIcon(normal_icon)
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)
        # Add buttons
        buttons = [
            self.min_button,
            self.normal_button,
            self.max_button,
            self.close_button,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(20, 20))
            button.setStyleSheet(
                """QToolButton {
                    border: none;
                    padding: 4px;
                }
                """
            )
            title_bar_layout.addWidget(button)
        title_bar_layout.setContentsMargins(20,10,10,0)

    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)

class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        self.app = app
        self.setWindowTitle("Your Daily Feed")
        self.resize(700, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        central_widget = QWidget()

        central_widget.setObjectName("Container")
        central_widget.setStyleSheet(
            """#Container {
            background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #051c2a stop:1 #44315f);
            border-radius: 20px;
        }"""
        )
        self.title_bar = CustomTitleBar(self)

        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.load_weather_twitter_fact_ui(content_layout)
        self.load_news_ui(content_layout)
        self.load_forex_ui(content_layout)
        self.load_nasa_picture_ui(content_layout)
        self.load_number_fact_of_the_day_ui(content_layout)
        self.load_dog_cat_fact_ui(content_layout)
        self.load_football_ui(content_layout)
        self.load_linkedin_jobs_ui(content_layout)

        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(5)

        # Scrollable content
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet(
            """background-color: #28282B;
                border-style: outset;
                border-width: 0px;
                border-radius: 20px;
                border-color: black;
                padding: 3px""")
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.scroll_area.setGraphicsEffect(effect)
        self.scroll_area.setWidgetResizable(True)

        # Main layout
        work_space_layout = QVBoxLayout()
        work_space_layout.setContentsMargins(11, 11, 11, 11)
        work_space_layout.addWidget(self.scroll_area)
        
        central_widget_layout = QVBoxLayout()
        central_widget_layout.setContentsMargins(0, 0, 0, 0)
        central_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        central_widget_layout.addWidget(self.title_bar)
        central_widget_layout.addLayout(work_space_layout)

        central_widget.setLayout(central_widget_layout)
        self.setCentralWidget(central_widget)

        self.show()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()

    def window_state_changed(self, state):
        self.normal_button.setVisible(state == Qt.WindowState.WindowMaximized)
        self.max_button.setVisible(state != Qt.WindowState.WindowMaximized)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()

# ------------------- Content Functions -------------------

    def load_weather_twitter_fact_ui(self, layout):
        horizontal_layout = QHBoxLayout()

        # --- CARD 1 ---
        card_widget_1 = QWidget()
        card_layout_1 = QHBoxLayout(card_widget_1)
        weather_background = os.path.join("weather_image.jpg")
        card_widget_1.setStyleSheet(f"""
                background-image: url("{weather_background}");
                background-repeat: no-repeat;
                background-position: center;
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")

        horizontal_layout_k = QHBoxLayout()

        left_vertical_layout = QVBoxLayout()
        label = QLabel(f"{current_temp}°C")
        label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        font = QFont("Arial", 25)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(10)
        label.setGraphicsEffect(effect)
        left_vertical_layout.addWidget(label)
        label = QLabel(f"Feels Like: {current_feels_like_temp}°C")
        label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_vertical_layout.addWidget(label)

        horizontal_layout_k.addLayout(left_vertical_layout)

        right_vertical_layout = QVBoxLayout()
        label = QLabel(f"   Rain: {current_rain_global} mm")
        label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        right_vertical_layout.addWidget(label)
        label = QLabel(f"   Daily Max Temp: {daily_temperature_max}°C")
        label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        right_vertical_layout.addWidget(label)
        label = QLabel(f"   Daily Min Temp: {daily_temperature_min}°C")
        label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        right_vertical_layout.addWidget(label)
        label.setFixedSize(220, 25)

        horizontal_layout_k.addLayout(right_vertical_layout)
        card_layout_1.addLayout(horizontal_layout_k)

        # --- CARD 2 ---

        card_widget_2 = QWidget()
        card_layout_2 = QHBoxLayout(card_widget_2)
        card_widget_2.setStyleSheet(f"""
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #26a7de, stop:1 #e3f0fa);
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")

        right_card_layout = QHBoxLayout()
        twitter_trending_label = QLabel("Twitter \nTrending")
        twitter_trending_label.setStyleSheet("background-color: transparent;")
        twitter_trending_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = twitter_trending_label.font()
        font.setPointSize(14)
        font.setBold(True)
        twitter_trending_label.setFont(font)
        right_card_layout.addWidget(twitter_trending_label)

        font = QFont()
        font.setPointSize(13)
        font.setBold(True)

        trending_list = QListWidget()
        trending_list.setStyleSheet(f"""
                background-color: #1B1B1B;
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")
        
        for trend in range(3):
            trend_item = QListWidgetItem(str(' #' + trending_topics[trend]))
            trend_item.setFont(font)
            trend_item.setForeground(QBrush(QColor('#FAF9F6')))
            trending_list.addItem(trend_item)
            
        trending_list.setFixedSize(150, 80)
        right_card_layout.addWidget(trending_list)

        card_layout_2.addLayout(right_card_layout)

        horizontal_layout.addWidget(card_widget_1)
        horizontal_layout.addWidget(card_widget_2)
        layout.addLayout(horizontal_layout)

    def load_weather_ui(self, layout):
        
        card_widget = QWidget()
        card_layout = QVBoxLayout(card_widget)
        weather_background = os.path.join("weather_image.jpg")
        card_widget.setStyleSheet(f"""
                background-image: url({weather_background});
                background-repeat: no-repeat;
                background-position: center;
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")
        
        weather_label = QLabel("Weather")
        weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = weather_label.font()
        font.setPointSize(14)
        font.setBold(True)
        weather_label.setFont(font)

        horizontal_layout = QHBoxLayout()

        left_vertical_layout = QVBoxLayout()
        label = QLabel(f"{current_temp}°C")
        font = QFont("Arial", 25)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(10)
        label.setGraphicsEffect(effect)
        left_vertical_layout.addWidget(label)
        label = QLabel(f"Feels Like: {current_feels_like_temp}°C")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_vertical_layout.addWidget(label)

        horizontal_layout.addLayout(left_vertical_layout)

        right_vertical_layout = QVBoxLayout()
        label = QLabel(f"Rain: {current_rain_global} mm")
        right_vertical_layout.addWidget(label)
        label = QLabel(f"Daily Max Temp: {daily_temperature_max}°C")
        right_vertical_layout.addWidget(label)
        label = QLabel(f"Daily Min Temp: {daily_temperature_min}°C")
        right_vertical_layout.addWidget(label)

        horizontal_layout.addLayout(right_vertical_layout)
        card_layout.addLayout(horizontal_layout)

        for child in card_widget.children():
            if isinstance(child, QLabel):
                child.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")

        layout.addWidget(card_widget)

    def load_news_ui(self, layout):

        card_widget = QWidget()
        card_layout = QVBoxLayout(card_widget)
        card_widget.setStyleSheet("""
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #c0392b, stop:1 #800000);
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")

        news_label = QLabel("Breaking News")
        news_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = news_label.font()
        font.setPointSize(16)
        font.setBold(True)
        news_label.setFont(font)
        card_layout.addWidget(news_label)

        for index in range(3):

            mini_card_widget = QWidget()
            mini_card_layout = QVBoxLayout(mini_card_widget)
            mini_card_widget.setStyleSheet("""
                    background-color: white;
                    border-radius: 15px;
                    padding: 2px;""")

            label = QLabel(f"{headlines[index]}")
            label.setWordWrap(True)
            font = label.font()
            font.setBold(True)
            label.setFont(font)
            mini_card_layout.addWidget(label)
            label = QLabel(f"Source: {source_name[index]}")
            mini_card_layout.addWidget(label)
            label = QLabel(f"{headline_description[index]}")
            label.setWordWrap(True)
            mini_card_layout.addWidget(label)
            label = QLabel(f"Link: {headline_url[index]}")
            label.setWordWrap(True)
            mini_card_layout.addWidget(label)
            card_layout.addWidget(mini_card_widget)

        for child in card_widget.children():
            if isinstance(child, QLabel):
                child.setStyleSheet("background-color: transparent;")
        
        layout.addWidget(card_widget)

    def load_forex_ui(self, layout):
        card_widget = QWidget()
        card_layout = QVBoxLayout(card_widget)
        card_widget.setStyleSheet(
            """background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #2ecc71, stop:1 #f1c40f);
                border-radius: 10px;
                border-color: black;
                padding: 3px""")
        
        forex_label = QLabel("Forex")
        forex_label.setStyleSheet("background-color: transparent; color: black;")
        forex_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = forex_label.font()
        font.setPointSize(16)
        font.setBold(True)
        forex_label.setFont(font)
        card_layout.addWidget(forex_label)

        horizontal_layout = QHBoxLayout()

        for currency, value in currency_dict.items():
            currency_container = QWidget()
            currency_container.setFixedWidth(185)
            currency_layout = QVBoxLayout(currency_container)
            currency_container.setStyleSheet(
                """background-color: #1B1B1B;
                    border-radius: 10px;
                    border-color: black;
                    padding: 10px;""")
            
            pair_label = QLabel(currency)
            pair_label.setStyleSheet("background-color: transparent; color: white; font-weight: bold;")
            pair_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            currency_layout.addWidget(pair_label)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("background-color: transparent; color: white;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            currency_layout.addWidget(value_label)
            
            horizontal_layout.addWidget(currency_container)

        card_layout.addLayout(horizontal_layout)
        layout.addWidget(card_widget)

    def load_nasa_picture_ui(self, layout):

        card_widget = QWidget()
        card_layout = QVBoxLayout(card_widget)
        card_widget.setStyleSheet("""
                background: qlineargradient(x1:0 y1:0, x2:1 y1:0, stop:0 #2155cd, stop:1 #87ceeb);
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")

        image_section = QLabel("NASA Image of the day")
        image_section.setStyleSheet("background-color: transparent;")
        image_section.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = image_section.font()
        font.setPointSize(16)
        font.setBold(True)
        image_section.setFont(font)
        card_layout.addWidget(image_section)

        image_title_label = QLabel(image_title)
        image_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(image_title_label)

        image_path = os.path.join(os.path.dirname(__file__), "image_of_the_day")
        image_pixmap = QPixmap(image_path)
        image_pixmap = image_pixmap.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio)
        
        image_label = QLabel()
        image_label.setPixmap(image_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""border-radius: 15px;""")

        card_layout.addWidget(image_label)

        image_title_desc = QLabel(image_description)
        image_title_desc.setWordWrap(True)
        image_title_desc.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(image_title_desc)

        layout.addWidget(card_widget)

    def load_number_fact_of_the_day_ui(self, layout):

        card_widget = QWidget()
        card_layout = QVBoxLayout(card_widget)
        card_widget.setStyleSheet("""
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #FFC0CB, stop:1 #D938BD);
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")

        news_label = QLabel("Number fact of the day")
        news_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = news_label.font()
        font.setPointSize(16)
        font.setBold(True)
        news_label.setFont(font)
        card_layout.addWidget(news_label)

        number_fact = api_server.fetch_number_fact_of_the_day()
        label = QLabel(f"{number_fact}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        card_layout.addWidget(label)

        for child in card_widget.children():
            if isinstance(child, QLabel):
                child.setStyleSheet("background-color: transparent;")

        layout.addWidget(card_widget)

    def load_dog_cat_fact_ui(self, layout):

        dog_fact, cat_fact = api_server.fetch_random_dog_cat_fact()

        horizontal_layout = QHBoxLayout()

        card_widget_1 = QWidget()
        card_layout_1 = QHBoxLayout(card_widget_1)
        dog_picture = os.path.join("dog_image.jpg")
        card_widget_1.setStyleSheet(f"""
                background-image: url("{dog_picture}");
                background-repeat: no-repeat;
                background-position: center;
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")
        

        #--- CARD 1 ---
        
        vertical_layout_1 = QVBoxLayout()
        dog_fact_label = QLabel("Dog Fact \U0001F436")
        dog_fact_label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        dog_fact_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        font = dog_fact_label.font()
        font.setPointSize(20)
        font.setBold(True)
        dog_fact_label.setFont(font)
        vertical_layout_1.addWidget(dog_fact_label)

        label = QLabel(f"{dog_fact}")
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label.setWordWrap(True)
        vertical_layout_1.addWidget(label)

        card_layout_1.addLayout(vertical_layout_1)

        # --- CARD 2 ---

        card_widget_2 = QWidget()
        card_layout_2 = QHBoxLayout(card_widget_2)
        cat_picture = os.path.join("cat_image.jpg")
        card_widget_2.setStyleSheet(f"""
                background-image: url("{cat_picture}");
                background-repeat: no-repeat;
                background-position: center;
                border-radius: 10px;
                border-color: black;
                padding: 3px;""")

        vertical_layout_2 = QVBoxLayout()
        cat_fact_label = QLabel("\U0001F408 Cat Fact")
        cat_fact_label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        cat_fact_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = cat_fact_label.font()
        font.setPointSize(20)
        font.setBold(True)
        cat_fact_label.setFont(font)
        vertical_layout_2.addWidget(cat_fact_label)

        label = QLabel(f"{cat_fact}")
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("background-image: url('transparent.png'); background-color: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        label.setWordWrap(True)
        vertical_layout_2.addWidget(label)

        card_layout_2.addLayout(vertical_layout_2)

        horizontal_layout.addWidget(card_widget_1)
        horizontal_layout.addWidget(card_widget_2)
        layout.addLayout(horizontal_layout)

    def load_football_ui(self, layout):

        card_widget = QWidget()
        card_layout = QVBoxLayout(card_widget)
        card_widget.setStyleSheet(
            """background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #3498db, stop:1 #9b59b6);
                border-radius: 10px;
                border-color: black;
                padding: 3px""")
        sports_label = QLabel("Football")
        sports_label.setStyleSheet("background-color: transparent; color: white;")
        sports_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = sports_label.font()
        font.setPointSize(16)
        font.setBold(True)
        sports_label.setFont(font)
        card_layout.addWidget(sports_label)

        for match in range(3):
            match_widget = QWidget()
            match_layout = QHBoxLayout(match_widget)
            match_widget.setStyleSheet(
                """background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #2ecc71, stop:1 #f1c40f);
                    border-radius: 10px;
                    border-color: black;
                    padding: 10px;""")
            
            match_label = QLabel(match_teams[match])
            match_label.setStyleSheet("background-color: transparent;")
            match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            match_layout.addWidget(match_label)
            
            date_label = QLabel(match_date[match])
            date_label.setStyleSheet("background-color: transparent;")
            date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            match_layout.addWidget(date_label)
            
            time_label = QLabel(match_time[match])
            time_label.setStyleSheet("background-color: transparent;")
            time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            match_layout.addWidget(time_label)
            
            location_label = QLabel(match_stadium[match])
            location_label.setStyleSheet("background-color: transparent;")
            location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            match_layout.addWidget(location_label)
            
            card_layout.addWidget(match_widget)

        layout.addWidget(card_widget)

    def load_linkedin_jobs_ui(self, layout):
        card_widget = QWidget()
        card_layout = QVBoxLayout(card_widget)
        card_widget.setStyleSheet(
            """background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #0077b5, stop:1 #005582);
                border-radius: 10px;
                border-color: black;
                padding: 3px""")
        
        jobs_label = QLabel("LinkedIn Job Listings")
        jobs_label.setStyleSheet("background-color: transparent; color: white;")
        jobs_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = jobs_label.font()
        font.setPointSize(16)
        font.setBold(True)
        jobs_label.setFont(font)
        card_layout.addWidget(jobs_label)

        jobs_container = QWidget()
        jobs_layout = QHBoxLayout(jobs_container)
        jobs_container.setStyleSheet("background-color: transparent;")

        for job in range(3):
            job_widget = QWidget()
            job_widget.setFixedWidth(185)
            job_layout = QVBoxLayout(job_widget)
            job_widget.setStyleSheet(
                """background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #289bd2, stop:1 #0077b5);
                    border-radius: 10px;
                    border-color: black;
                    padding: 10px;""")
            
            title_label = QLabel(job_titles[job])
            title_label.setStyleSheet("background-color: transparent; color: white;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = title_label.font()
            font.setPointSize(12)
            font.setBold(True)
            title_label.setFont(font)
            job_layout.addWidget(title_label)
            
            company_label = QLabel(job_company[job])
            company_label.setStyleSheet("background-color: transparent; color: white;")
            company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            job_layout.addWidget(company_label)
            
            location_label = QLabel(job_location[job])
            location_label.setStyleSheet("background-color: transparent; color: white;")
            location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            job_layout.addWidget(location_label)

            title_label.setWordWrap(True)
            company_label.setWordWrap(True)
            location_label.setWordWrap(True)
            
            jobs_layout.addWidget(job_widget)

        card_layout.addWidget(jobs_container)
        layout.addWidget(card_widget)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(window.app.exec())
    