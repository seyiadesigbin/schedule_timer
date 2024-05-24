import webbrowser

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QDialog, QMessageBox, QPushButton
from PySide6.QtGui import QIcon, QImage, QPixmap
from globals import (APP_TITLE, APP_ICON_DIR, APP_VERSION, load_stylesheet,
                     CLOSE_ICON_DIR, GITHUB_ICON_DIR, LINKEDIN_ICON_DIR, WHATSAPP_ICON_DIR)
from PySide6.QtCore import Qt

TOOLBAR_STYLESHEET_FILE_NAME = "tool_bar_stylesheet.qss"
GITHUB_URL = "https://github.com/seyiadesigbin"
LINKEDIN_URL = "https://www.linkedin.com/in/seyiadesigbin/"
WHATSAPP_URL = "https://wa.me/message/I4P7NA44QNFTK1?src=qr"

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        pass


class AboutDialog(QWidget):
    """Window to display details about the application"""
    def __init__(self):
        super().__init__()

        self.stylesheet = load_stylesheet(TOOLBAR_STYLESHEET_FILE_NAME)
        self.setWindowFlag(Qt.FramelessWindowHint | Qt.Tool)
        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(APP_ICON_DIR))
        self.setFixedSize(400, 200)
        self.setObjectName("background")
        self.setStyleSheet(self.stylesheet)

        window_layout = QVBoxLayout()

        # Create row for the title
        title_row_layout = QHBoxLayout()
        title_row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_row_layout.setSpacing(0)

        app_icon_label = QLabel()
        app_icon = QPixmap(APP_ICON_DIR)
        app_icon = app_icon.scaled(40, 40)
        app_icon_label.setPixmap(app_icon)

        # title_label = QLabel(f"{APP_TITLE} {APP_VERSION}")
        title_label = QLabel(f"{APP_TITLE}")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        close_button = QPushButton()
        close_button.setIcon(QIcon(CLOSE_ICON_DIR))
        close_button.clicked.connect(self.close_window)
        close_button.setObjectName("cancelButton")

        title_row_layout.addWidget(app_icon_label)
        title_row_layout.addWidget(title_label)
        title_row_layout.addStretch()
        title_row_layout.addWidget(close_button)

        description_row_layout = QHBoxLayout()
        description_row_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        description_text = QLabel()
        description_text.setTextFormat(Qt.RichText)
        description_text.setText(f"<b>{APP_TITLE}</b> is a free software designed to help you seamlessly manage"
                                 f" timing during your <b>church</b> service or other events.")
        description_text.setWordWrap(True)
        description_text.setObjectName("description")
        description_text.setAlignment(Qt.AlignmentFlag.AlignTop)

        contact_row = QHBoxLayout()

        github_button = QPushButton()
        github_button.setIcon(QIcon(GITHUB_ICON_DIR))
        github_button.clicked.connect(lambda: self.open_pages("github"))

        linkedin_button = QPushButton()
        linkedin_button.setIcon(QIcon(LINKEDIN_ICON_DIR))
        linkedin_button.clicked.connect(lambda: self.open_pages("linkedin"))

        whatsapp_button = QPushButton()
        whatsapp_button.setIcon(QIcon(WHATSAPP_ICON_DIR))
        whatsapp_button.clicked.connect(lambda: self.open_pages("whatsapp"))

        designed_by_text = QLabel()
        designed_by_text.setTextFormat(Qt.RichText)
        designed_by_text.setText("<b>Developed by</b>: Oluwaseyi Adesigbin")

        contact_row.addWidget(linkedin_button)
        contact_row.addWidget(github_button)
        contact_row.addWidget(whatsapp_button)

        window_layout.addLayout(title_row_layout)
        window_layout.addWidget(description_text)
        window_layout.addWidget(designed_by_text)
        window_layout.addLayout(contact_row)

        self.setLayout(window_layout)

    def close_window(self):
        self.close()

    def open_pages(self, platform):
        """Opens a url in the web browser"""
        url = ""

        if platform == "github":
            url = GITHUB_URL
        elif platform == "linkedin":
            url = LINKEDIN_URL
        elif platform == "whatsapp":
            url = WHATSAPP_URL

        webbrowser.open(url)


class CreditsDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.stylesheet = load_stylesheet(TOOLBAR_STYLESHEET_FILE_NAME)
        self.setWindowFlag(Qt.FramelessWindowHint | Qt.Tool)
        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(APP_ICON_DIR))
        self.setFixedSize(400, 200)
        self.setObjectName("background")
        self.setStyleSheet(self.stylesheet)




