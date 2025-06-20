import os

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtLocation import QPlaceIcon  # This might not be needed, consider removing if not used later
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QProgressBar, QGroupBox,
    QStackedWidget, QLineEdit, QButtonGroup, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from .base_widget import BaseWidget

# Import the backend steganography module
from backend.steganography import DCTSteganography

# Get absolute path to assets
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")


class EncryptionScreen(BaseWidget):
    def __init__(self, switch_callback):
        self.switch_callback = switch_callback
        super().__init__()

        # --- New instance variables to store selected data ---
        self.cover_image_path = None
        self.secret_text_to_embed = None
        self.secret_file_path = None
        self.secret_file_content = None  # Stores content as bytes
        # ----------------------------------------------------

        # Initialize the DCTSteganography backend
        self.stego = DCTSteganography()

        self.init_ui()

    def init_ui(self):
        self.encrypt_main_holder = QWidget(self)
        self.encrypt_main_holder.setGeometry(0, 0, 900, 700)
        self.encrypt_main_holder.setStyleSheet("background: rgba(0, 0, 0, 200);")
        self.encrypt_main_holder_layout = QHBoxLayout(self.encrypt_main_holder)
        self.encrypt_main_holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.encrypt_main_holder_layout.setSpacing(10)

        # Stacked widget for image cover selection
        self.encrypt_main_stack = QStackedWidget(self)
        self.encrypt_main_stack.setStyleSheet("background: transparent;")
        self.encrypt_main_stack.setFixedSize(370, 480)
        self.encrypt_main_holder_layout.addWidget(self.encrypt_main_stack)

        # section where the cover image is set (Page 0 of encrypt_main_stack)
        self.encrypt_main_ = QWidget(self)
        self.encrypt_main_.setGeometry(0, 0, 370, 480)
        self.encrypt_main_.setStyleSheet("background: rgb(14, 14, 15); border: 1px solid #81C8FF; border-radius: 35px;")
        self.encrypt_main_layout = QVBoxLayout(self.encrypt_main_)
        self.encrypt_main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.encrypt_main_layout.setSpacing(15)
        self.encrypt_main_layout.setContentsMargins(10, 50, 10, 20)
        self.encrypt_main_stack.addWidget(self.encrypt_main_)

        self.encrypt_indicator_label = QLabel(self)
        self.encrypt_indicator_label.setText("Image Encryption")
        self.encrypt_indicator_label.setStyleSheet("color: #ffffee; font-size: 20px; border: none;")
        self.encrypt_indicator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.encrypt_indicator_comment = QLabel(self)
        self.encrypt_indicator_comment.setText("Encrypt your images in just three simple steps")
        self.encrypt_indicator_comment.setStyleSheet("color: #6A7788; font-size: 12px; border: none;")

        self.encrypt_progress = QProgressBar(self)
        self.encrypt_progress.setFixedSize(200, 5)
        self.encrypt_progress.setStyleSheet("background: transparent; border: none;")
        self.encrypt_progress.setValue(0)  # Initial progress at 0
        self.encrypt_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.encrypt_dropbox = QGroupBox()
        self.encrypt_dropbox.setFixedSize(270, 180)
        self.encrypt_dropbox.setStyleSheet("border: 2px dashed grey; border-radius: 0; background-color: black; ")
        self.encrypt_dropbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Stacked widget for image cover selection states (upload vs. confirmed)
        self.encrypt_box_stack = QStackedWidget(self.encrypt_dropbox)
        self.encrypt_box_stack.setStyleSheet("background: transparent;")
        self.encrypt_box_stack.setGeometry(0, 0, 270, 180)


        # Default upload state (Page 0 of encrypt_box_stack)
        self.encrypt_dropbox_inner = QWidget(self.encrypt_box_stack)
        self.encrypt_dropbox_inner.setGeometry(40, 35, 190, 110)
        self.encrypt_dropbox_inner.setStyleSheet("border: none; background-color: transparent;")
        self.encrypt_box_stack.addWidget(self.encrypt_dropbox_inner)
        self.encrypt_dropbox_inner_layout = QVBoxLayout(self.encrypt_dropbox_inner)
        self.encrypt_dropbox_inner_layout.setSpacing(8)
        self.encrypt_dropbox_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_label = QLabel(self.encrypt_dropbox_inner)
        logo_pixmap = QPixmap(os.path.join(ASSETS_PATH, "upload-icon-3.png")).scaled(  # Use ASSETS_PATH
            25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.upload_label.setPixmap(logo_pixmap)
        self.upload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.enc_label_1 = QLabel(self.encrypt_dropbox_inner)
        self.enc_label_1.setText("Tap to upload image")
        self.enc_label_1.setStyleSheet("color: #81C8FF; font-size: 12px; font-weight: bold")
        self.enc_label_1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.enc_label_2 = QLabel(self.encrypt_dropbox_inner)
        self.enc_label_2.setText("PNG, JPEG Max(5mb)")  # Note: PDF is not supported for image cover
        self.enc_label_2.setStyleSheet("color: #6A7788; font-size: 10px;")
        self.enc_label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_cover_img_btn = QPushButton(self.encrypt_dropbox_inner)
        self.upload_cover_img_btn.setGeometry(40, 35, 190, 110)
        self.upload_cover_img_btn.clicked.connect(self._select_cover_image)
        self.upload_cover_img_btn.setStyleSheet("""
                    background: transparent;
                    border: none;
                """)

        self.encrypt_dropbox_inner_layout.addWidget(self.upload_label)
        self.encrypt_dropbox_inner_layout.addWidget(self.enc_label_1)
        self.encrypt_dropbox_inner_layout.addWidget(self.enc_label_2)

        # Confirm or reset selected image section (Page 1 of encrypt_box_stack)
        self.encrypt_dropbox_confirm = QWidget(self)
        self.encrypt_dropbox_confirm.setStyleSheet("border: none; background-color: transparent;")
        self.encrypt_box_stack.addWidget(self.encrypt_dropbox_confirm)
        self.encrypt_dropbox_confirm_layout = QVBoxLayout(self.encrypt_dropbox_confirm)
        self.encrypt_dropbox_confirm_layout.setSpacing(8)
        self.encrypt_dropbox_confirm_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cover_img_label = QLabel(self.encrypt_dropbox_confirm)
        self.cover_img_label.setFixedSize(120, 120)
        self.cover_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_img_label.setStyleSheet("border: 1px solid #81C8FF;")

        self.comfirm_img_label = QLabel(self.encrypt_dropbox_confirm)
        self.comfirm_img_label.setText("Upload Completed")
        self.comfirm_img_label.setStyleSheet("color: #FFFFEE; font-size: 12px; font-weight: bold")
        self.comfirm_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.selected_cover_filename_label = QLabel(self.encrypt_dropbox_confirm)
        self.selected_cover_filename_label.setStyleSheet("color: #6A7788; font-size: 10px;")
        self.selected_cover_filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_cover_filename_label.setWordWrap(True)

        self.delete_img_btn = QPushButton(self.encrypt_dropbox_confirm)
        self.delete_img_btn.setFixedSize(150, 25)
        self.delete_img_btn.setText("  Clear Upload")
        self.delete_img_btn.setIcon(QPixmap(os.path.join(ASSETS_PATH, "delete_icon.png")).scaled(12, 12))
        self.delete_img_btn.setIconSize(QSize(12, 12))
        self.delete_img_btn.clicked.connect(self._clear_cover_image)
        self.delete_img_btn.setStyleSheet("""
                            color: #6A7788;
                            font-size: 12px;
                            min-width: 120px;
                            background: transparent;
                            border: none;
                        """)

        self.encrypt_dropbox_confirm_layout.addWidget(self.cover_img_label)
        self.encrypt_dropbox_confirm_layout.addWidget(self.comfirm_img_label)
        self.encrypt_dropbox_confirm_layout.addWidget(self.selected_cover_filename_label)
        self.encrypt_dropbox_confirm_layout.addWidget(self.delete_img_btn)

        self.encrypt_btn_hold = QWidget(self)
        self.encrypt_btn_hold.setFixedSize(270, 50)
        self.encrypt_btn_hold.setStyleSheet("border: none; border-radius: 0;")
        self.encrypt_btn_hold_layout = QHBoxLayout(self.encrypt_btn_hold)
        self.encrypt_btn_hold_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.encrypt_img_btn = QPushButton(self)
        self.encrypt_img_btn.setFixedSize(150, 40)
        self.encrypt_img_btn.setText("</> Encrypt Image")
        self.encrypt_img_btn.clicked.connect(self._proceed_to_embed_section)
        self.encrypt_img_btn.setStyleSheet("""
                    color: #FFFFFF;
                    font-size: 14px;
                    padding: 12px 20px;
                    min-width: 120px;
                    background: #3B82F6;
                    border: none;
                    border-radius: 20px;
                """)
        self.encrypt_btn_hold_layout.addWidget(self.encrypt_img_btn)

        self.encrypt_main_layout.addWidget(self.encrypt_indicator_label)
        self.encrypt_main_layout.addWidget(self.encrypt_indicator_comment)
        self.encrypt_main_layout.addWidget(self.encrypt_progress)
        self.encrypt_main_layout.addWidget(self.encrypt_dropbox)
        self.encrypt_main_layout.addWidget(self.encrypt_btn_hold)

        self.close_encrypt_btn = QPushButton(self.encrypt_main_)
        self.close_encrypt_btn.setText("✕")
        self.close_encrypt_btn.setGeometry(320, 20, 30, 30)
        self.close_encrypt_btn.clicked.connect(lambda: self.switch_callback("home"))
        self.close_encrypt_btn.setStyleSheet("""
            color: #FFFFFF;
            font-size: 16px;
            background: transparent;
            border: none;
        """)

        self.label_4tag = QLabel(self)
        self.label_4tag.setText("© 2025, Quoin-lab Technology")
        self.label_4tag.setStyleSheet("color: #ffffee; font-size: 12px;")
        self.label_4tag.setGeometry(710, 620, 200, 35)

        # ===================================================================================
        # section where the message/document is embedded (Page 1 of encrypt_main_stack)
        self.encrypt_main_2 = QWidget(self)
        self.encrypt_main_2.setGeometry(0, 0, 370, 480)
        self.encrypt_main_2.setStyleSheet(
            "background: rgb(14, 14, 15); border: 1px solid #81C8FF; border-radius: 35px;")
        self.encrypt_main_layout2 = QVBoxLayout(self.encrypt_main_2)
        self.encrypt_main_layout2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.encrypt_main_layout2.setSpacing(15)
        self.encrypt_main_layout2.setContentsMargins(10, 50, 10, 20)
        self.encrypt_main_stack.addWidget(self.encrypt_main_2)

        # Title and description
        self.encrypt_indicator_label2 = QLabel(self.encrypt_main_2)
        self.encrypt_indicator_label2.setText("Image Encryption")
        self.encrypt_indicator_label2.setStyleSheet("color: #ffffee; font-size: 20px; border: none;")
        self.encrypt_indicator_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.encrypt_indicator_comment2 = QLabel(self.encrypt_main_2)
        self.encrypt_indicator_comment2.setText("Embed a document in your uploaded image")
        self.encrypt_indicator_comment2.setStyleSheet("color: #6A7788; font-size: 12px; border: none;")
        self.encrypt_indicator_comment2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress bar
        self.encrypt_progress2 = QProgressBar(self.encrypt_main_2)
        self.encrypt_progress2.setFixedSize(200, 5)
        self.encrypt_progress2.setStyleSheet("background: transparent; border: none;")
        self.encrypt_progress2.setValue(0)  # Initial progress at 0
        self.encrypt_progress2.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Switchable buttons (Document/Text)
        self.file_text_switch = QWidget(self.encrypt_main_2)
        self.file_text_switch.setFixedSize(250, 38)
        self.file_text_switch.setStyleSheet("background: black; border: none; border-radius: 14px;")
        self.switch_layout = QHBoxLayout(self.file_text_switch)
        self.switch_layout.setContentsMargins(2, 2, 2, 2)
        self.switch_layout.setSpacing(0)

        self.btn_encode_doc = QPushButton("Encode Document", self.file_text_switch)
        self.btn_encode_doc.setCheckable(True)
        self.btn_encode_doc.setChecked(True)
        self.btn_encode_doc.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 30);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 5px;
            }
            QPushButton:checked {
                background: rgba(255, 255, 255, 60);
            }
        """)
        self.btn_encode_doc.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_encode_text = QPushButton("Encode Text", self.file_text_switch)
        self.btn_encode_text.setCheckable(True)
        self.btn_encode_text.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 5px;
            }
            QPushButton:checked {
                background: rgba(255, 255, 255, 60);
            }
        """)
        self.btn_encode_text.setCursor(Qt.CursorShape.PointingHandCursor)

        self.switch_layout.addWidget(self.btn_encode_doc)
        self.switch_layout.addWidget(self.btn_encode_text)

        self.switch_group = QButtonGroup(self.file_text_switch)
        self.switch_group.addButton(self.btn_encode_doc)
        self.switch_group.addButton(self.btn_encode_text)
        self.switch_group.setExclusive(True)

        self.content_stack = QStackedWidget(self.encrypt_main_2)
        self.content_stack.setFixedWidth(300)
        self.content_stack.setStyleSheet("border: none; border-radius: 0; background-color: transparent;")

        # ===== Document Mode Content =====
        self.doc_widget = QWidget()
        self.doc_layout = QVBoxLayout(self.doc_widget)
        self.doc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doc_layout.setSpacing(10)

        # Dropbox for documents
        self.encrypt_dropbox2 = QGroupBox()
        self.encrypt_dropbox2.setFixedSize(270, 140)
        self.encrypt_dropbox2.setStyleSheet("border: 2px dashed grey; border-radius: 0; background-color: black;")
        self.encrypt_dropbox2_layout = QVBoxLayout(self.encrypt_dropbox2)
        self.encrypt_dropbox2_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container for initial upload prompt or selected file info
        self.doc_upload_state_stack = QStackedWidget(self.encrypt_dropbox2)
        self.doc_upload_state_stack.setStyleSheet("background: transparent; border: none;")
        self.doc_upload_state_stack.setFixedSize(270, 140)  # Match dropbox size
        self.encrypt_dropbox2_layout.addWidget(self.doc_upload_state_stack)

        # Page 0: Initial upload prompt for documents
        self.doc_upload_prompt_widget = QWidget()
        self.doc_upload_prompt_layout = QVBoxLayout(self.doc_upload_prompt_widget)
        self.doc_upload_prompt_layout.setSpacing(8)
        self.doc_upload_prompt_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_label2 = QLabel(self.doc_upload_prompt_widget)
        logo_pixmap = QPixmap(os.path.join(ASSETS_PATH, "upload-icon-3.png")).scaled(
            25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.upload_label2.setPixmap(logo_pixmap)
        self.upload_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.enc_label_11 = QLabel(self.doc_upload_prompt_widget)
        self.enc_label_11.setText("Tap to upload document")
        self.enc_label_11.setStyleSheet("color: #81C8FF; font-size: 12px; font-weight: bold")
        self.enc_label_11.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.enc_label_21 = QLabel(self.doc_upload_prompt_widget)
        self.enc_label_21.setText("Any file type. Max size depends on image.")
        self.enc_label_21.setStyleSheet("color: #6A7788; font-size: 10px;")
        self.enc_label_21.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_doc_btn = QPushButton(self.doc_upload_prompt_widget)
        self.upload_doc_btn.setGeometry(0, 0, 270, 140)
        self.upload_doc_btn.clicked.connect(self._select_document_file)
        self.upload_doc_btn.setStyleSheet("""
                            background: transparent;
                            border: none;
                        """)
        self.doc_upload_prompt_layout.addWidget(self.upload_label2)
        self.doc_upload_prompt_layout.addWidget(self.enc_label_11)
        self.doc_upload_prompt_layout.addWidget(self.enc_label_21)
        self.doc_upload_state_stack.addWidget(self.doc_upload_prompt_widget)

        # Page 1: Display selected document info
        self.doc_selected_info_widget = QWidget()
        self.doc_selected_info_layout = QVBoxLayout(self.doc_selected_info_widget)
        self.doc_selected_info_layout.setSpacing(5)
        self.doc_selected_info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.doc_icon_label = QLabel(self.doc_selected_info_widget)
        self.doc_icon_label.setPixmap(QPixmap(os.path.join(ASSETS_PATH, "file_icon.png")).scaled(40, 40))
        self.doc_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.doc_filename_label = QLabel(self.doc_selected_info_widget)
        self.doc_filename_label.setStyleSheet("color: #FFFFEE; font-size: 12px; font-weight: bold;")
        self.doc_filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doc_filename_label.setWordWrap(True)

        self.doc_size_label = QLabel(self.doc_selected_info_widget)
        self.doc_size_label.setStyleSheet("color: #6A7788; font-size: 10px;")
        self.doc_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.doc_clear_btn = QPushButton("Clear Document", self.doc_selected_info_widget)
        self.doc_clear_btn.setFixedSize(120, 25)
        self.doc_clear_btn.setStyleSheet("""
            QPushButton {
                color: #6A7788;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        self.doc_clear_btn.setIcon(QPixmap(os.path.join(ASSETS_PATH, "delete_icon.png")).scaled(12, 12))
        self.doc_clear_btn.setIconSize(QSize(12, 12))
        self.doc_clear_btn.clicked.connect(self._clear_document_file)

        self.doc_selected_info_layout.addWidget(self.doc_icon_label)
        self.doc_selected_info_layout.addWidget(self.doc_filename_label)
        self.doc_selected_info_layout.addWidget(self.doc_size_label)
        self.doc_selected_info_layout.addWidget(self.doc_clear_btn)
        self.doc_upload_state_stack.addWidget(self.doc_selected_info_widget)

        # Password input for document
        self.doc_password_frame = QWidget()
        self.doc_password_layout = QHBoxLayout(self.doc_password_frame)
        self.doc_password_layout.setContentsMargins(0, 0, 0, 0)

        self.doc_password_input = QLineEdit()
        self.doc_password_input.setPlaceholderText("Enter encryption password...")
        self.doc_password_input.setFixedHeight(35)
        self.doc_password_input.setStyleSheet("""
            QLineEdit {
                background: black;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.doc_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.doc_toggle_eye = QPushButton()
        self.doc_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "show.png")))
        self.doc_toggle_eye.setIconSize(QSize(25, 25))
        self.doc_toggle_eye.setStyleSheet("background: transparent; border: none;")
        self.doc_toggle_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self.doc_toggle_eye.clicked.connect(self._toggle_doc_password)

        self.doc_password_layout.addWidget(self.doc_password_input)
        self.doc_password_layout.addWidget(self.doc_toggle_eye)

        # Embed document button
        self.btn_embed_doc = QPushButton("</> Embed Document")
        self.btn_embed_doc.setFixedSize(200, 35)
        self.btn_embed_doc.clicked.connect(self._embed_document_clicked)
        self.btn_embed_doc.setStyleSheet("""
            QPushButton {
                background: #81C8FF;
                color: black;
                border: none;
                border-radius: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #6AB0E0;
            }
        """)

        # Add widgets to document layout
        self.doc_layout.addWidget(self.encrypt_dropbox2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.doc_layout.addWidget(self.doc_password_frame)
        self.doc_layout.addWidget(self.btn_embed_doc, alignment=Qt.AlignmentFlag.AlignCenter)

        # ===== Text Mode Content =====
        self.text_widget = QWidget()
        self.text_layout = QVBoxLayout(self.text_widget)
        self.text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_layout.setSpacing(15)

        # Text edit area
        self.text_edit = QTextEdit()
        self.text_edit.setFixedSize(270, 140)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: black;
                color: white;
                border: 1px solid grey;
                padding: 5px;
            }
        """)
        self.text_edit.setPlaceholderText("Enter text to embed here...")
        self.text_edit.textChanged.connect(self._update_secret_text)

        # Password input for text
        self.text_password_frame = QWidget()
        self.text_password_layout = QHBoxLayout(self.text_password_frame)
        self.text_password_layout.setContentsMargins(0, 0, 0, 0)

        self.text_password_input = QLineEdit()
        self.text_password_input.setPlaceholderText("Enter encryption password")
        self.text_password_input.setFixedHeight(35)
        self.text_password_input.setStyleSheet("""
            QLineEdit {
                background: black;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.text_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.text_toggle_eye = QPushButton()
        self.text_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "show.png")))
        self.text_toggle_eye.setIconSize(QSize(25, 25))
        self.text_toggle_eye.setStyleSheet("background: transparent; border: none;")
        self.text_toggle_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self.text_toggle_eye.clicked.connect(self._toggle_text_password)

        self.text_password_layout.addWidget(self.text_password_input)
        self.text_password_layout.addWidget(self.text_toggle_eye)

        # Embed text button
        self.btn_embed_text = QPushButton("Embed Text")
        self.btn_embed_text.setFixedSize(200, 35)
        self.btn_embed_text.clicked.connect(self._embed_text_clicked)
        self.btn_embed_text.setStyleSheet("""
            QPushButton {
                background: #81C8FF;
                color: black;
                border: none;
                border-radius: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #6AB0E0;
            }
        """)

        # Add widgets to text layout
        self.text_layout.addWidget(self.text_edit, alignment=Qt.AlignmentFlag.AlignCenter)
        self.text_layout.addWidget(self.text_password_frame)
        self.text_layout.addWidget(self.btn_embed_text, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add both modes to the stack
        self.content_stack.addWidget(self.doc_widget)
        self.content_stack.addWidget(self.text_widget)

        # Connect switch buttons to change the stack
        def switch_mode():
            if self.btn_encode_doc.isChecked():
                self.content_stack.setCurrentIndex(0)
            else:
                self.content_stack.setCurrentIndex(1)

        self.btn_encode_doc.clicked.connect(switch_mode)
        self.btn_encode_text.clicked.connect(switch_mode)

        # Toggle password visibility functions
        self.doc_toggle_eye.clicked.connect(self._toggle_doc_password)
        self.text_toggle_eye.clicked.connect(self._toggle_text_password)

        # Add all widgets to main layout
        self.encrypt_main_layout2.addWidget(self.encrypt_indicator_label2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.encrypt_main_layout2.addWidget(self.encrypt_indicator_comment2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.encrypt_main_layout2.addWidget(self.encrypt_progress2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.encrypt_main_layout2.addWidget(self.file_text_switch, alignment=Qt.AlignmentFlag.AlignCenter)
        self.encrypt_main_layout2.addWidget(self.content_stack, alignment=Qt.AlignmentFlag.AlignCenter)

        self.close_encrypt_btn = QPushButton(self.encrypt_main_2)
        self.close_encrypt_btn.setGeometry(25, 20, 30, 30)
        self.close_encrypt_btn.setIcon(QPixmap(os.path.join(ASSETS_PATH, "arrow_left.png")))
        self.close_encrypt_btn.setIconSize(QSize(16, 16))
        self.close_encrypt_btn.clicked.connect(lambda: self.switch_encryption_section(0))
        self.close_encrypt_btn.setStyleSheet("""
                    font-size: 16px;
                    background: transparent;
                    border: none;
                """)

    def switch_image_selector(self, index: int):
        """Switches the stacked widget for cover image display."""
        self.encrypt_box_stack.setCurrentIndex(index)

    def switch_encryption_section(self, index: int):
        """Switches the main stacked widget between cover image selection and embedding options."""
        self.encrypt_main_stack.setCurrentIndex(index)

    def _select_cover_image(self):
        """Opens a file dialog to select the cover image (PNG/JPEG) and updates UI."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        file_dialog.setWindowTitle("Select Cover Image")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.cover_image_path = selected_files[0]

                pixmap = QPixmap(self.cover_image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.cover_img_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.cover_img_label.setPixmap(scaled_pixmap)
                    self.comfirm_img_label.setText("Image Selected!")
                    self.selected_cover_filename_label.setText(os.path.basename(self.cover_image_path))
                    self.switch_image_selector(1)
                else:
                    QMessageBox.warning(self, "Image Error", "Could not load selected image.")
                    self._clear_cover_image()
            else:
                self._clear_cover_image()

    def _clear_cover_image(self):
        """Clears the selected cover image and resets UI."""
        self.cover_image_path = None
        self.cover_img_label.clear()
        self.comfirm_img_label.setText("Upload Completed")
        self.selected_cover_filename_label.setText("")
        self.switch_image_selector(0)

    def _proceed_to_embed_section(self):
        """Checks if a cover image is selected before proceeding to the next section."""
        if self.cover_image_path:
            self.switch_encryption_section(1)
            self.encrypt_progress2.setValue(0)  # Reset progress for embedding
        else:
            QMessageBox.warning(self, "No Cover Image", "Please select a cover image before proceeding.")

    def _select_document_file(self):
        """Opens a file dialog to select any document/file for embedding."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("All Files (*.*)")
        file_dialog.setWindowTitle("Select Document to Embed")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.secret_file_path = selected_files[0]
                try:
                    with open(self.secret_file_path, 'rb') as f:
                        self.secret_file_content = f.read()

                    self.doc_filename_label.setText(os.path.basename(self.secret_file_path))
                    file_size_bytes = len(self.secret_file_content)
                    if file_size_bytes < 1024:
                        self.doc_size_label.setText(f"{file_size_bytes} Bytes")
                    elif file_size_bytes < (1024 * 1024):
                        self.doc_size_label.setText(f"{file_size_bytes / 1024:.2f} KB")
                    else:
                        self.doc_size_label.setText(f"{file_size_bytes / (1024 * 1024):.2f} MB")

                    self.doc_upload_state_stack.setCurrentIndex(1)

                except Exception as e:
                    QMessageBox.warning(self, "File Read Error", f"Could not read selected file: {e}")
                    self._clear_document_file()
            else:
                self._clear_document_file()

    def _clear_document_file(self):
        """Clears the selected document file and resets UI."""
        self.secret_file_path = None
        self.secret_file_content = None
        self.doc_filename_label.setText("")
        self.doc_size_label.setText("")
        self.doc_upload_state_stack.setCurrentIndex(0)

    def _update_secret_text(self):
        """Updates the stored secret text whenever the QTextEdit content changes."""
        self.secret_text_to_embed = self.text_edit.toPlainText()

    def _toggle_doc_password(self):
        """Toggles visibility of the document password."""
        if self.doc_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.doc_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.doc_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "hide_.png")))
        else:
            self.doc_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.doc_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "show.png")))

    def _toggle_text_password(self):
        """Toggles visibility of the text password."""
        if self.text_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.text_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.text_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "hide_.png")))
        else:
            self.text_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.text_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "show.png")))

    def _embed_document_clicked(self):
        """
        Handler for the 'Embed Document' button.
        Calls backend steganography to embed a file.
        """
        password = self.doc_password_input.text()
        if not self.cover_image_path:
            QMessageBox.warning(self, "Missing Input", "Please select a cover image first.")
            return
        if not self.secret_file_content:
            QMessageBox.warning(self, "Missing Input", "Please select a document to embed.")
            return
        if not password:
            QMessageBox.warning(self, "Missing Input", "Please enter an encryption password.")
            return

        # Get the output path for the stego image from a file dialog
        output_stego_path, _ = QFileDialog.getSaveFileName(self, "Save Stego Image", "stego_document.png",
                                                           "PNG Images (*.png);;All Files (*.*)")
        if not output_stego_path:
            QMessageBox.warning(self, "Save Cancelled", "Stego image not saved.")
            return

        try:
            # Call the backend embed_data function
            # The secret_file_content is already bytes
            self.stego.embed_data(
                image_path=self.cover_image_path,
                secret_data=self.secret_file_content,
                password=password,
                is_text=False,
                original_filename=os.path.basename(self.secret_file_path),  # Pass original filename for metadata
                output_path=output_stego_path  # Pass the determined output path here
            )
            QMessageBox.information(self, "Embedding Complete",
                                    f"Document embedded successfully into {output_stego_path}")
            # Optionally clear inputs after successful embedding
            self._clear_cover_image()
            self._clear_document_file()
            self.doc_password_input.clear()
            self.switch_encryption_section(0)  # Go back to image selection
        except ValueError as ve:
            QMessageBox.critical(self, "Embedding Error", f"Embedding failed: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred during embedding: {e}")

    def _embed_text_clicked(self):
        """
        Handler for the 'Embed Text' button.
        Calls backend steganography to embed text.
        """
        password = self.text_password_input.text()
        if not self.cover_image_path:
            QMessageBox.warning(self, "Missing Input", "Please select a cover image first.")
            return
        if not self.secret_text_to_embed:
            QMessageBox.warning(self, "Missing Input", "Please enter text to embed.")
            return
        if not password:
            QMessageBox.warning(self, "Missing Input", "Please enter an encryption password.")
            return

        # Get the output path for the stego image from a file dialog
        output_stego_path, _ = QFileDialog.getSaveFileName(self, "Save Stego Image", "stego_text.png",
                                                           "PNG Images (*.png);;All Files (*.*)")
        if not output_stego_path:
            QMessageBox.warning(self, "Save Cancelled", "Stego image not saved.")
            return

        try:
            # Call the backend embed_data function
            # The secret_text_to_embed is a string
            self.stego.embed_data(
                image_path=self.cover_image_path,
                secret_data=self.secret_text_to_embed,
                password=password,
                is_text=True,
                output_path=output_stego_path  # Pass the determined output path here
            )
            QMessageBox.information(self, "Embedding Complete", f"Text embedded successfully into {output_stego_path}")
            # Optionally clear inputs after successful embedding
            self._clear_cover_image()
            self.text_edit.clear()
            self.text_password_input.clear()
            self.secret_text_to_embed = None  # Reset stored text
            self.switch_encryption_section(0)  # Go back to image selection
        except ValueError as ve:
            QMessageBox.critical(self, "Embedding Error", f"Embedding failed: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred during embedding: {e}")

