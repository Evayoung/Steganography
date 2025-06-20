# frontend/home.py
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt
from .base_widget import BaseWidget

class HomeScreen(BaseWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback
        self.init_ui()


    def init_ui(self):

        self.top_holder = QWidget(self)
        self.top_holder.setGeometry(100, 50, 700, 100)
        self.top_holder_layout = QHBoxLayout(self.top_holder)
        self.top_holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.top_holder_layout.setSpacing(10)

        self.first_label = QLabel(self)
        self.first_label.setText("Secure")
        # self.first_label.setGeometry(320, 70, 100, 70)
        self.first_label.setStyleSheet("color: #ffffee; font-size: 42px;")

        self.second_label = QLabel(self)
        self.second_label.setText("secrets,")
        #self.second_label.setGeometry(460, 70, 200, 70)
        self.second_label.setStyleSheet("color: #81C8FF; font-size: 42px; font-style: italic;")

        self.top_holder_layout.addWidget(self.first_label)
        self.top_holder_layout.addWidget(self.second_label)

        self.top_holder2 = QWidget(self)
        self.top_holder2.setGeometry(100, 95, 700, 100)
        self.top_holder2_layout = QHBoxLayout(self.top_holder2)
        self.top_holder2_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.top_holder2_layout.setSpacing(10)

        self.third_label = QLabel(self)
        self.third_label.setText("seamlessly hidden.")
        # self.third_label.setGeometry(400, 150, 200, 70)
        self.third_label.setStyleSheet("color: #ffffee; font-size: 42px;")

        self.top_holder2_layout.addWidget(self.third_label)

        self.second_holder = QWidget(self)
        self.second_holder.setGeometry(100, 170, 700, 60)
        self.second_holder_layout = QVBoxLayout(self.second_holder)
        self.second_holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.second_holder_layout.setSpacing(2)

        self.label_small1 = QLabel(self)
        self.label_small1.setText("Securely hide messages or files in images with seamless, invincible encryption")
        self.label_small1.setStyleSheet("color: #6A7788; font-size: 16px;")

        self.label_small2 = QLabel(self)
        self.label_small2.setText("Easy, private, undetectable")
        self.label_small2.setStyleSheet("color: #6A7788; font-size: 16px;")
        self.label_small2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.second_holder_layout.addWidget(self.label_small1)
        self.second_holder_layout.addWidget(self.label_small2)

        self.button_holder = QWidget(self)
        self.button_holder.setGeometry(100, 250, 700, 60)
        self.button_holder_layout = QHBoxLayout(self.button_holder)
        self.button_holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_holder_layout.setSpacing(15)

        self.start_btn = QPushButton(self)
        self.start_btn.setText("Start Encryption")
        self.start_btn.setFixedHeight(45)
        self.start_btn.clicked.connect(lambda: self.switch_callback("encryption"))
        self.start_btn.setStyleSheet("""
            color: #FFFFFF;
            font-size: 14px;
            padding: 12px 20px;
            min-width: 120px;
            background: #3B82F6;
            border: none;
            border-radius: 22px;
        """)

        self.decrypt_btn = QPushButton(self)
        self.decrypt_btn.setText("Decrypt an Image")
        self.decrypt_btn.setFixedHeight(45)
        self.decrypt_btn.clicked.connect(lambda: self.switch_callback("decryption"))
        self.decrypt_btn.setStyleSheet("""
                    color: #ffffee;
                    font-size: 14px;
                    padding: 10px 20px;
                    min-width: 120px;
                    background: transparent;
                    border: 2px solid #0D2E63;
                    border-radius: 22px;
                """)

        self.button_holder_layout.addWidget(self.start_btn)
        self.button_holder_layout.addWidget(self.decrypt_btn)

        self.bottom_holder = QWidget(self)
        self.bottom_holder.setGeometry(100, 560, 700, 100)
        self.bottom_holder_layout = QVBoxLayout(self.bottom_holder)
        self.bottom_holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottom_holder_layout.setSpacing(5)

        self.bottom_label = QLabel(self)
        self.bottom_label.setText("Invisible security for the digital age.")
        self.bottom_label.setStyleSheet("color: #ffffee; font-size: 20px;")
        #self.bottom_label.setMinimumHeight(80)
        self.bottom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bottom_label1 = QLabel(self)
        self.bottom_label1.setText("In a world full of digital threats, Stego gives you a safe way to share what")
        self.bottom_label1.setStyleSheet("color: #6A7788; font-size: 12px;")

        self.bottom_label2 = QLabel(self)
        self.bottom_label2.setText("matters without leaving a trace")
        self.bottom_label2.setStyleSheet("color: #6A7788; font-size: 12px;")
        self.bottom_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bottom_holder_layout.addWidget(self.bottom_label)
        self.bottom_holder_layout.addWidget(self.bottom_label1)
        self.bottom_holder_layout.addWidget(self.bottom_label2)