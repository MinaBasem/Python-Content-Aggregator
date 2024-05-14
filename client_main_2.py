from PyQt6.QtCore import QEvent, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QMainWindow,
    QToolButton,
    QWidget,
    QGraphicsDropShadowEffect,
    QScrollArea
)
from socket import *
import os
import sys
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import (Qt, QSize, QUrl)

import api_server

api_server.start_data_threads()
#api_server.fetch_image_of_the_day()
from api_server import current_temp, current_feels_like_temp, current_rain_global, daily_temperature_max, daily_temperature_min
from api_server import headlines, source_name, headline_description, headline_url
from api_server import currencies, currency_pairs, currency_pairs_values
from api_server import image_data
from api_server import number_fact
from api_server import dog_fact, cat_fact

#box_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

scroll_bar_config = """
/* VERTICAL SCROLLBAR */
 QScrollArea:vertical {
	border: none;
    background: rgb(45, 45, 68);
    width: 14px;
    margin: 15px 0 15px 0;
	border-radius: 0px;
 }

/*  HANDLE BAR VERTICAL */
QScrollArea::handle:vertical {	
	background-color: rgb(80, 80, 122);
	min-height: 30px;
	border-radius: 7px;
}
QScrollArea::handle:vertical:hover{	
	background-color: rgb(255, 0, 127);
}
QScrollArea::handle:vertical:pressed {	
	background-color: rgb(185, 0, 92);
}

/* BTN TOP - SCROLLBAR */
QScrollArea::sub-line:vertical {
	border: none;
	background-color: rgb(59, 59, 90);
	height: 15px;
	border-top-left-radius: 7px;
	border-top-right-radius: 7px;
	subcontrol-position: top;
	subcontrol-origin: margin;
}
QScrollArea::sub-line:vertical:hover {	
	background-color: rgb(255, 0, 127);
}
QScrollArea::sub-line:vertical:pressed {	
	background-color: rgb(185, 0, 92);
}

/* BTN BOTTOM - SCROLLBAR */
QScrollArea::add-line:vertical {
	border: none;
	background-color: rgb(59, 59, 90);
	height: 15px;
	border-bottom-left-radius: 7px;
	border-bottom-right-radius: 7px;
	subcontrol-position: bottom;
	subcontrol-origin: margin;
}
QScrollArea::add-line:vertical:hover {	
	background-color: rgb(255, 0, 127);
}
QScrollArea::add-line:vertical:pressed {	
	background-color: rgb(185, 0, 92);
}

/* RESET ARROW */
QScrollArea::up-arrow:vertical, QScrollArea::down-arrow:vertical {
	background: none;
}
QScrollArea::add-page:vertical, QScrollArea::sub-page:vertical {
	background: none;
}



/* HORIZONTAL SCROLLBAR - HOMEWORK */
QScrollArea:horizontal {
   
}
QScrollArea::handle:horizontal {
    
}
QScrollArea::add-line:horizontal {
    
}
QScrollArea::sub-line:horizontal {
    
}
QScrollArea::up-arrow:horizontal, QScrollArea::down-arrow:horizontal
{

}
QScrollArea::add-page:horizontal, QScrollArea::sub-page:horizontal
{

}"""


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

app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = app
        self.setWindowTitle("Your Daily Feed")
        self.resize(600, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        central_widget = QWidget()

        #background: qlineargradient(x1:0 y1:0, x2:1 y1:0, stop:0 #87ceeb, stop:1 #007bff);
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

        self.load_weather_ui(content_layout)
        self.load_news_ui(content_layout)
        self.load_forex_ui(content_layout)
        self.load_nasa_picture_ui(content_layout)
        self.load_number_fact_of_the_day_ui(content_layout)
        self.load_dog_cat_fact_ui(content_layout)

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
        #self.scroll_area.setStyleSheet(scroll_bar_config)
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


    def load_weather_ui(self, layout):
        
        card_widget = QWidget()
        card_layout = QVBoxLayout(card_widget)
        weather_background = os.path.join("weather_image.jpg")
        #background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #f1c40f, stop:1 #2196f3);
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
        #card_layout.addWidget(weather_label)

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

        image_label = QLabel()
        image_pixmap = QPixmap("sun.png")
        image_pixmap = image_pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(image_pixmap)
        horizontal_layout.addWidget(image_label)

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

        #api_server.fetch_news_api()
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
        forex_label.setStyleSheet("background-color: transparent;")
        forex_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = forex_label.font()
        font.setPointSize(16)
        font.setBold(True)
        forex_label.setFont(font)
        card_layout.addWidget(forex_label)

        #api_server.fetch_forex_api()
        horizontal_layout = QHBoxLayout()

        for currency in range(5):
            #label = QLabel(f"Pair: {currencies[currency]}")
            vertical_layout = QVBoxLayout()
            label = QLabel("Pair: 30")
            label.setStyleSheet("background-color: transparent;")
            vertical_layout.addWidget(label)
            #label = QLabel(f"Value: {currency_pairs_values[currency]}")
            label = QLabel("Value: 50")
            label.setStyleSheet("background-color: transparent;")
            vertical_layout.addWidget(label)
            horizontal_layout.addLayout(vertical_layout)

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

        image_path = os.path.join(os.path.dirname(__file__), "image_of_the_day")
        image_pixmap = QPixmap(image_path)
        image_pixmap = image_pixmap.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio)
        
        image_label = QLabel()
        image_label.setPixmap(image_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""border-radius: 15px;""")

        card_layout.addWidget(image_label)
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

if __name__ == "__main__":
    window = MainWindow()
    window.show()
    sys.exit(window.app.exec())