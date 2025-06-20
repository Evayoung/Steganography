import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, \
    QTextBrowser, QPushButton  # Using QTextBrowser for rich text
from PySide6.QtCore import Qt, QSize
from .base_widget import BaseWidget

# Get absolute path to assets
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")


class AboutScreen(BaseWidget):
    def __init__(self, switch_callback):
        self.switch_callback = switch_callback
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.about_main_holder = QWidget(self)
        self.about_main_holder.setGeometry(0, 0, 900, 670)
        self.about_main_holder.setStyleSheet("background: rgba(0, 0, 0, 200);")
        self.about_main_holder_layout = QHBoxLayout(self.about_main_holder)
        self.about_main_holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.about_main_holder_layout.setSpacing(10)

        self.about_main_ = QWidget()
        self.about_main_.setMinimumSize(600, 450)  # Increased size for more content
        self.about_main_.setStyleSheet("background: rgb(14, 14, 15); border: 1px solid #81C8FF; border-radius: 25px;")
        self.about_main_layout = QVBoxLayout(self.about_main_)
        self.about_main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.about_main_layout.setSpacing(20)  # Increased spacing
        self.about_main_layout.setContentsMargins(40, 40, 40, 40)  # Increased margins
        self.about_main_holder_layout.addWidget(self.about_main_)

        # Use QTextBrowser for rich text (HTML/Markdown-like)
        self.about_content_browser = QTextBrowser()
        self.about_content_browser.setReadOnly(True)
        self.about_content_browser.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                color: #ffffee;
                font-size: 14px;
                border: none;
            }
            h2 {
                color: #81C8FF;
                font-size: 24px;
                margin-bottom: 10px;
            }
            p {
                margin-bottom: 10px;
            }
            strong {
                color: #FFFFFF;
            }
        """)

        about_text = """
        <h2>About Stego</h2>
        <p>Welcome to <strong>Stego</strong>, a cutting-edge steganography application developed by <strong>Quoin-lab Technologies</strong>. In an increasingly interconnected digital world, privacy and secure communication are paramount. Stego is designed to provide an invisible layer of security, allowing you to embed confidential messages and files directly within images, completely unnoticed by casual observers.</p>

        <p>At <strong>Quoin-lab Technologies</strong>, we are dedicated to crafting innovative solutions that empower individuals and organizations with robust digital security. Stego embodies our commitment to this mission, offering a seamless and intuitive experience for advanced data hiding.</p>

        <h3>Our Technology</h3>
        <p>Stego employs a sophisticated <strong>Hybrid Discrete Cosine Transform (DCT) and Least Significant Bit (LSB)</strong> steganography technique, fortified with strong <strong>AES-256 encryption</strong>. This dual-layer approach ensures both:
        <ul>
            <li><strong>Imperceptibility:</strong> Your hidden data causes minimal visual impact on the cover image.</li>
            <li><strong>Robustness:</strong> The embedded information can withstand certain common image manipulations.</li>
            <li><strong>Confidentiality:</strong> Even if detected, your hidden message remains unreadable without the correct decryption key.</li>
        </ul>
        We've meticulously engineered Stego to overcome common challenges in steganography, providing a reliable and secure method for covert communication.</p>

        <h3>Our Vision</h3>
        <p>Quoin-lab Technologies envisions a digital landscape where secure and private communication is accessible to everyone. Stego is a step towards realizing that vision, offering peace of mind in a world full of digital threats. Share what matters without leaving a trace.</p>

        <p align="center">Thank you for choosing Stego.<br/>
        &copy; 2025, Quoin-lab Technologies</p>
        """
        self.about_content_browser.setHtml(about_text)

        self.about_main_layout.addWidget(self.about_content_browser)

        self.close_about_btn = QPushButton(self.about_main_)
        self.close_about_btn.setText("✕")
        self.close_about_btn.setGeometry(550, 20, 30, 30)  # Adjusted position for larger widget
        self.close_about_btn.clicked.connect(lambda: self.switch_callback("home"))
        self.close_about_btn.setStyleSheet("""
            color: #FFFFFF;
            font-size: 16px;
            background: transparent;
            border: none;
        """)