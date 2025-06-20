# main.py
from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget,
                               QHBoxLayout, QPushButton, QLabel, QWidget,
                               QVBoxLayout, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QKeySequence, QPixmap, QColor
import sys
import warnings
import os
from frontend import HomeScreen, EncryptionScreen, DecryptionScreen, AboutScreen

# Suppress SIP deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganography App")
        self.setMinimumSize(900, 720)  # More balanced minimum size
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Main widget with transparent background
        main_widget = QWidget()
        main_widget.setObjectName("MainWidget")
        main_widget.setStyleSheet("""
            #MainWidget {
                background: transparent;
            }
        """)

        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        # Navigation bar - now with semi-transparent dark background
        self.nav_widget = QWidget()
        self.nav_widget.setObjectName("NavWidget")
        self.nav_widget.setFixedHeight(50)
        self.nav_widget.setStyleSheet("""
            #NavWidget {
                background-color: rgb(12, 13, 14);
                
            }
        """)

        self.nav_layout = QHBoxLayout(self.nav_widget)
        self.nav_layout.setContentsMargins(10, 0, 10, 0)
        self.nav_layout.setSpacing(20)

        # Logo
        self.logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join("assets", "steg_logo.png")).scaled(
            60, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setFixedSize(60, 50)
        self.nav_layout.addWidget(self.logo_label)

        # Spacer to push buttons to left and window controls to right
        spacer = QSpacerItem(60, 5, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.nav_layout.addItem(spacer)

        # Nav buttons with better styling
        button_styles = """
            QPushButton {
                color: #FFFFFF;
                font-size: 14px;
                padding: 8px 10px;
                background: transparent;
                border: none;
                min-width: 40px;
            }
            QPushButton:hover {
                color: #3B82F6;
            }
        """

        self.nav_buttons = {}
        for screen, label in [("home", "Home"), ("encryption", "Encrypt"),
                              ("decryption", "Decrypt"), ("about", "About")]:
            btn = QPushButton(label)
            btn.setStyleSheet(button_styles)
            btn.clicked.connect(lambda checked, s=screen: self.switch_screen(s))
            self.nav_buttons[screen] = btn
            self.nav_layout.addWidget(btn)



        # Window controls
        self.minimize_btn = QPushButton("–")
        self.minimize_btn.setFixedSize(30, 30)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)

        window_btn_style = """
            QPushButton {
                color: #FFFFFF;
                font-size: 16px;
                background: transparent;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 30);
            }
            QPushButton#closeBtn:hover {
                background: #FF5555;
            }
        """
        self.minimize_btn.setStyleSheet(window_btn_style)
        self.close_btn.setStyleSheet(window_btn_style + " #closeBtn:hover { background: #FF5555; }")
        self.close_btn.setObjectName("closeBtn")

        self.minimize_btn.clicked.connect(self.showMinimized)
        self.close_btn.clicked.connect(QApplication.quit)

        self.nav_layout.addWidget(self.minimize_btn)
        self.nav_layout.addWidget(self.close_btn)

        # Stacked widget for screens
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")

        self.screens = {
            "home": HomeScreen(self.switch_screen),
            "encryption": EncryptionScreen(self.switch_screen),
            "decryption": DecryptionScreen(self.switch_screen),
            "about": AboutScreen(self.switch_screen)
        }

        for name, widget in self.screens.items():
            self.stack.addWidget(widget)

        # Active indicator (initially hidden)
        self.indicator = QLabel(self.nav_widget)
        self.indicator.setFixedHeight(3)
        self.indicator.setStyleSheet("background-color: #3B82F6;")
        self.indicator.hide()

        # Add to main layout
        self.main_layout.addWidget(self.nav_widget)
        self.main_layout.addWidget(self.stack)

        # Set initial screen
        self.switch_screen("home")

        # Dragging variables
        self.dragging = False
        self.drag_position = QPoint()

    def switch_screen(self, screen_name):
        if screen_name in self.screens:
            self.stack.setCurrentWidget(self.screens[screen_name])
            btn = self.nav_buttons[screen_name]

            # Update indicator position
            btn_rect = btn.geometry()
            self.indicator.setFixedWidth(btn_rect.width() - 20)
            self.indicator.move(btn_rect.left() + 10, btn_rect.bottom() - 3)
            self.indicator.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < self.nav_widget.height():
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.pos()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Quit):
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style for consistent look
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(30, 30, 40))
    palette.setColor(palette.ColorRole.WindowText, Qt.GlobalColor.white)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())