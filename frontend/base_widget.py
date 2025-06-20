from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter
import os

# Get absolute path to assets
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")

class BaseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.background = QPixmap(os.path.join(ASSETS_PATH, "steg_bg3.png"))
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)
        super().paintEvent(event)