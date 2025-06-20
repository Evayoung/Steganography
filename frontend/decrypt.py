import os
from PySide6.QtGui import QPixmap, QIcon, QClipboard
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QProgressBar, QGroupBox,
    QStackedWidget, QLineEdit, QFileDialog, QMessageBox, QApplication, QTextEdit
)
from PySide6.QtCore import Qt, QSize, QByteArray
from .base_widget import BaseWidget

# Import the backend steganography module
from backend.steganography import DCTSteganography

# Get absolute path to assets
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")


class DecryptionScreen(BaseWidget):
    def __init__(self, switch_callback):
        self.switch_callback = switch_callback
        super().__init__()

        # --- Instance variables for decryption state ---
        self.stego_image_path = None
        self.decrypted_raw_data = None  # Stores decrypted bytes (either text or file)
        self.decrypted_is_text = False  # Flag: True if content is text, False if binary file
        self.suggested_filename = "extracted_content"  # Base name for downloaded files

        # Initialize the DCTSteganography backend
        self.stego = DCTSteganography()

        self.init_ui()

    def init_ui(self):
        self.decrypt_main_holder = QWidget(self)
        self.decrypt_main_holder.setGeometry(0, 0, 900, 700)
        self.decrypt_main_holder.setStyleSheet("background: rgba(0, 0, 0, 200);")
        self.decrypt_main_holder_layout = QHBoxLayout(self.decrypt_main_holder)
        self.decrypt_main_holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_holder_layout.setSpacing(10)

        # Stacked widget for initial image selection vs. decryption results
        self.decrypt_main_stack = QStackedWidget(self)
        self.decrypt_main_stack.setStyleSheet("background: transparent;")
        self.decrypt_main_stack.setFixedSize(370, 480)
        self.decrypt_main_holder_layout.addWidget(self.decrypt_main_stack)

        # --- Page 0: Stego Image Selection and Password Input ---
        self.decrypt_main_ = QWidget(self)
        self.decrypt_main_.setGeometry(0, 0, 370, 480)
        self.decrypt_main_.setStyleSheet("background: rgb(14, 14, 15); border: 1px solid #81C8FF; border-radius: 35px;")
        self.decrypt_main_layout = QVBoxLayout(self.decrypt_main_)
        self.decrypt_main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_layout.setSpacing(15)
        self.decrypt_main_layout.setContentsMargins(10, 50, 10, 20)
        self.decrypt_main_stack.addWidget(self.decrypt_main_)

        self.decrypt_indicator_label = QLabel(self)
        self.decrypt_indicator_label.setText("Image Decryption")
        self.decrypt_indicator_label.setStyleSheet("color: #ffffee; font-size: 20px; border: none;")
        self.decrypt_indicator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.decrypt_indicator_comment = QLabel(self)
        self.decrypt_indicator_comment.setText("Select image to extract hidden data")
        self.decrypt_indicator_comment.setStyleSheet("color: #6A7788; font-size: 12px; border: none;")
        self.decrypt_indicator_comment.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.decrypt_progress = QProgressBar(self)
        self.decrypt_progress.setFixedSize(200, 5)
        self.decrypt_progress.setStyleSheet("background: transparent; border: none;")
        self.decrypt_progress.setValue(0)  # Start at 0
        self.decrypt_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.decrypt_dropbox = QGroupBox()
        self.decrypt_dropbox.setFixedSize(270, 180)
        self.decrypt_dropbox.setStyleSheet("border: 2px dashed grey; border-radius: 0; background-color: black; ")
        self.decrypt_dropbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Stacked widget for image selection states (upload vs. confirmed)
        self.decrypt_box_stack = QStackedWidget(self.decrypt_dropbox)
        self.decrypt_box_stack.setStyleSheet("background: transparent;")
        self.decrypt_box_stack.setGeometry(0, 0, 270, 180)

        # Default upload state (Page 0 of decrypt_box_stack)
        self.decrypt_dropbox_inner = QWidget(self.decrypt_box_stack)
        self.decrypt_dropbox_inner.setGeometry(40, 35, 190, 110)
        self.decrypt_dropbox_inner.setStyleSheet("border: none; background-color: transparent;")
        self.decrypt_box_stack.addWidget(self.decrypt_dropbox_inner)
        self.decrypt_dropbox_inner_layout = QVBoxLayout(self.decrypt_dropbox_inner)
        self.decrypt_dropbox_inner_layout.setSpacing(8)
        self.decrypt_dropbox_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_label = QLabel(self.decrypt_dropbox_inner)
        logo_pixmap = QPixmap(os.path.join(ASSETS_PATH, "upload-icon-3.png")).scaled(
            25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.upload_label.setPixmap(logo_pixmap)
        self.upload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dec_label_1 = QLabel(self.decrypt_dropbox_inner)
        self.dec_label_1.setText("Tap to upload image")
        self.dec_label_1.setStyleSheet("color: #81C8FF; font-size: 12px; font-weight: bold")
        self.dec_label_1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dec_label_2 = QLabel(self.decrypt_dropbox_inner)
        self.dec_label_2.setText("PNG, JPEG Max(5mb)")
        self.dec_label_2.setStyleSheet("color: #6A7788; font-size: 10px;")
        self.dec_label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_stego_img_btn = QPushButton(self.decrypt_dropbox_inner)
        self.upload_stego_img_btn.setGeometry(40, 35, 190, 110)
        self.upload_stego_img_btn.clicked.connect(self._select_stego_image)
        self.upload_stego_img_btn.setStyleSheet("""
                            background: transparent;
                            border: none;
                        """)

        self.decrypt_dropbox_inner_layout.addWidget(self.upload_label)
        self.decrypt_dropbox_inner_layout.addWidget(self.dec_label_1)
        self.decrypt_dropbox_inner_layout.addWidget(self.dec_label_2)

        # Confirmed image state (Page 1 of decrypt_box_stack)
        self.decrypt_dropbox_confirm = QWidget(self)
        self.decrypt_dropbox_confirm.setStyleSheet("border: none; background-color: transparent;")
        self.decrypt_box_stack.addWidget(self.decrypt_dropbox_confirm)
        self.decrypt_dropbox_confirm_layout = QVBoxLayout(self.decrypt_dropbox_confirm)
        self.decrypt_dropbox_confirm_layout.setSpacing(8)
        self.decrypt_dropbox_confirm_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cover_img_label = QLabel(self.decrypt_dropbox_confirm)
        self.cover_img_label.setFixedSize(120, 120)
        self.cover_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_img_label.setStyleSheet("border: 1px solid #81C8FF;")

        self.comfirm_img_label = QLabel(self.decrypt_dropbox_confirm)
        self.comfirm_img_label.setText("Stego Image Selected!")
        self.comfirm_img_label.setStyleSheet("color: #FFFFEE; font-size: 12px; font-weight: bold")
        self.comfirm_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.selected_cover_filename_label = QLabel(self.decrypt_dropbox_confirm)
        self.selected_cover_filename_label.setStyleSheet("color: #6A7788; font-size: 10px;")
        self.selected_cover_filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_cover_filename_label.setWordWrap(True)

        self.delete_img_btn = QPushButton(self.decrypt_dropbox_confirm)
        self.delete_img_btn.setFixedSize(150, 25)
        self.delete_img_btn.setText("  Clear Upload")
        self.delete_img_btn.setIcon(QPixmap(os.path.join(ASSETS_PATH, "delete_icon.png")).scaled(12, 12))
        self.delete_img_btn.setIconSize(QSize(12, 12))
        self.delete_img_btn.clicked.connect(self._clear_stego_image)
        self.delete_img_btn.setStyleSheet("""
                                    color: #6A7788;
                                    font-size: 12px;
                                    min-width: 120px;
                                    background: transparent;
                                    border: none;
                                """)

        self.decrypt_dropbox_confirm_layout.addWidget(self.cover_img_label)
        self.decrypt_dropbox_confirm_layout.addWidget(self.comfirm_img_label)
        self.decrypt_dropbox_confirm_layout.addWidget(self.selected_cover_filename_label)
        self.decrypt_dropbox_confirm_layout.addWidget(self.delete_img_btn)

        # Password input for decryption
        self.decrypt_password_frame = QWidget()
        self.decrypt_password_frame.setFixedWidth(270)
        self.decrypt_password_frame.setStyleSheet("background: transparent; border: none;")
        self.decrypt_password_layout = QHBoxLayout(self.decrypt_password_frame)
        self.decrypt_password_layout.setContentsMargins(0, 0, 0, 0)
        self.decrypt_password_input = QLineEdit()
        self.decrypt_password_input.setPlaceholderText("Enter decryption password...")
        self.decrypt_password_input.setFixedHeight(35)
        self.decrypt_password_input.setStyleSheet("""
            QLineEdit {
                background: black;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.decrypt_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.decrypt_toggle_eye = QPushButton()
        self.decrypt_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "show.png")))
        self.decrypt_toggle_eye.setIconSize(QSize(25, 25))
        self.decrypt_toggle_eye.setStyleSheet("background: transparent; border: none;")
        self.decrypt_toggle_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self.decrypt_toggle_eye.clicked.connect(self._toggle_decrypt_password)

        self.decrypt_password_layout.addWidget(self.decrypt_password_input)
        self.decrypt_password_layout.addWidget(self.decrypt_toggle_eye)

        self.decrypt_btn_hold = QWidget(self)
        self.decrypt_btn_hold.setFixedSize(270, 50)
        self.decrypt_btn_hold.setStyleSheet("border: none; border-radius: 0;")
        self.decrypt_btn_hold_layout = QHBoxLayout(self.decrypt_btn_hold)
        self.decrypt_btn_hold_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.decrypt_img_btn = QPushButton(self)
        self.decrypt_img_btn.setFixedSize(150, 40)
        self.decrypt_img_btn.setText("</> Decrypt Image")
        self.decrypt_img_btn.clicked.connect(self._decrypt_image_clicked)
        self.decrypt_img_btn.setStyleSheet("""
                            color: #FFFFFF;
                            font-size: 14px;
                            padding: 12px 20px;
                            min-width: 120px;
                            background: #3B82F6;
                            border: none;
                            border-radius: 20px;
                        """)
        self.decrypt_btn_hold_layout.addWidget(self.decrypt_img_btn)

        self.decrypt_main_layout.addWidget(self.decrypt_indicator_label)
        self.decrypt_main_layout.addWidget(self.decrypt_indicator_comment)
        self.decrypt_main_layout.addWidget(self.decrypt_progress)
        self.decrypt_main_layout.addWidget(self.decrypt_dropbox)
        self.decrypt_main_layout.addWidget(self.decrypt_password_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_layout.addWidget(self.decrypt_btn_hold)

        self.close_decrypt_btn = QPushButton(self.decrypt_main_)
        self.close_decrypt_btn.setText("✕")
        self.close_decrypt_btn.setGeometry(320, 20, 30, 30)
        self.close_decrypt_btn.clicked.connect(lambda: self.switch_callback("home"))
        self.close_decrypt_btn.setStyleSheet("""
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
        # --- Page 1: Decryption Results ---
        self.decrypt_main_2 = QWidget(self)
        self.decrypt_main_2.setGeometry(0, 0, 370, 480)
        self.decrypt_main_2.setStyleSheet(
            "background: rgb(14, 14, 15); border: 1px solid #70ED00; border-radius: 35px;")
        self.decrypt_main_layout2 = QVBoxLayout(self.decrypt_main_2)
        self.decrypt_main_layout2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_layout2.setSpacing(15)
        self.decrypt_main_layout2.setContentsMargins(10, 30, 10, 20)
        self.decrypt_main_stack.addWidget(self.decrypt_main_2)

        self.success_label = QLabel()
        logo_pixmap = QPixmap(os.path.join(ASSETS_PATH, "Group.png")).scaled(
            75, 75, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.success_label.setPixmap(logo_pixmap)
        self.success_label.setStyleSheet("border: none;")
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.decrypt_indicator_label2 = QLabel()
        self.decrypt_indicator_label2.setText("Decrypted Successfully!!")
        self.decrypt_indicator_label2.setStyleSheet("color: #ffffee; font-size: 20px; border: none;")
        self.decrypt_indicator_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.decrypt_indicator_comment2 = QLabel()
        self.decrypt_indicator_comment2.setText("Below is the data that was decrypted from the image")
        self.decrypt_indicator_comment2.setStyleSheet("color: #6A7788; font-size: 12px; border: none;")
        self.decrypt_indicator_comment2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.decrypted_text_edit = QTextEdit()
        self.decrypted_text_edit.setFixedSize(270, 140)
        self.decrypted_text_edit.setReadOnly(True)
        self.decrypted_text_edit.setStyleSheet("""
                    QTextEdit {
                        background: black;
                        color: white;
                        border: 1px solid grey;
                        padding: 5px;
                        border-radius: 0px;
                    }
                """)
        self.decrypted_text_edit.setPlaceholderText("Decrypted content will appear here...")

        self.result_action_btn = QPushButton("Action Button")
        self.result_action_btn.setFixedSize(120, 35)
        self.result_action_btn.setStyleSheet("""
            QPushButton {
                background: #6A7788;
                color: #ffffee;
                border: none;
                border-radius: 17px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #5A6778;
            }
        """)
        self.result_action_btn.clicked.connect(self._handle_result_action)

        self.back_home_btn = QPushButton("< Back Home")
        self.back_home_btn.setFixedSize(200, 35)
        self.back_home_btn.clicked.connect(lambda: self.switch_callback("home"))
        self.back_home_btn.setStyleSheet("""
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

        self.decrypt_main_layout2.addWidget(self.success_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_layout2.addWidget(self.decrypt_indicator_label2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_layout2.addWidget(self.decrypt_indicator_comment2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_layout2.addWidget(self.decrypted_text_edit, alignment=Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_layout2.addWidget(self.result_action_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.decrypt_main_layout2.addWidget(self.back_home_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.close_result_btn = QPushButton(self.decrypt_main_2)
        self.close_result_btn.setGeometry(25, 20, 30, 30)
        self.close_result_btn.setIcon(QPixmap(os.path.join(ASSETS_PATH, "arrow_left.png")))
        self.close_result_btn.setIconSize(QSize(16, 16))
        self.close_result_btn.clicked.connect(lambda: self.switch_decryption_section(0))
        self.close_result_btn.setStyleSheet("""
                            font-size: 16px;
                            background: transparent;
                            border: none;
                        """)

    def switch_decryption_section(self, index: int):
        """Switches the main stacked widget between image selection (0) and results display (1)."""
        self.decrypt_main_stack.setCurrentIndex(index)
        if index == 0:
            self._clear_decryption_results()
            self.decrypt_progress.setValue(0)

    def _select_stego_image(self):
        """Opens a file dialog to select the stego image (PNG/JPEG) for decryption."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Stego Images (*.png *.jpg *.jpeg)")
        file_dialog.setWindowTitle("Select Stego Image")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.stego_image_path = selected_files[0]

                pixmap = QPixmap(self.stego_image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.cover_img_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.cover_img_label.setPixmap(scaled_pixmap)
                    self.comfirm_img_label.setText("Stego Image Selected!")
                    self.selected_cover_filename_label.setText(os.path.basename(self.stego_image_path))
                    self.decrypt_box_stack.setCurrentIndex(1)
                else:
                    QMessageBox.warning(self, "Image Error", "Could not load selected image.")
                    self._clear_stego_image()
            else:
                self._clear_stego_image()

    def _clear_stego_image(self):
        """Clears the selected stego image and resets UI."""
        self.stego_image_path = None
        self.cover_img_label.clear()
        self.comfirm_img_label.setText("Upload Completed")
        self.selected_cover_filename_label.setText("")
        self.decrypt_box_stack.setCurrentIndex(0)

    def _toggle_decrypt_password(self):
        """Toggles visibility of the decryption password."""
        if self.decrypt_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.decrypt_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.decrypt_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "hide_.png")))
        else:
            self.decrypt_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.decrypt_toggle_eye.setIcon(QPixmap(os.path.join(ASSETS_PATH, "show.png")))

    def _decrypt_image_clicked(self):
        """
        Handler for the 'Decrypt Image' button.
        Calls backend steganography for decryption.
        """
        password = self.decrypt_password_input.text()
        if not self.stego_image_path:
            QMessageBox.warning(self, "Missing Input", "Please select a stego image first.")
            return
        if not password:
            QMessageBox.warning(self, "Missing Input", "Please enter a decryption password.")
            return

        QMessageBox.information(self, "Decrypting...",
                                f"Attempting to decrypt data from: {os.path.basename(self.stego_image_path)}\n"
                                f"Using provided password."
                                )
        try:
            # Call the backend extract_data function
            # This returns a dictionary with 'type', 'content', 'filename', 'file_extension'
            result = self.stego.extract_data(self.stego_image_path, password)
            self.decrypted_raw_data = result[self.stego.METADATA_KEY_CONTENT]  # Get the content (str or bytes)

            if result[self.stego.METADATA_KEY_TYPE] == self.stego.TEXT_TYPE:
                self.decrypted_text_edit.setText(self.decrypted_raw_data)  # Content is already string for text
                self.decrypted_is_text = True
                self.result_action_btn.setText("Copy Text")
            elif result[self.stego.METADATA_KEY_TYPE] == self.stego.FILE_TYPE:
                # Content is bytes for files
                self.decrypted_text_edit.setText(
                    "Binary file detected. Click 'Save File' to download.\n"
                    f"File size: {len(self.decrypted_raw_data)} bytes."
                )
                self.decrypted_is_text = False
                self.result_action_btn.setText("Save File")
                # Update suggested filename from metadata
                if self.stego.METADATA_KEY_FILENAME in result:
                    self.suggested_filename = result[self.stego.METADATA_KEY_FILENAME]
                elif self.stego.METADATA_KEY_FILEEXT in result:
                    # If only extension is available, combine with base image name
                    base_name = os.path.splitext(os.path.basename(self.stego_image_path))[0]
                    self.suggested_filename = f"{base_name}{result[self.stego.METADATA_KEY_FILEEXT]}"
                else:
                    self.suggested_filename = "extracted_content"  # Fallback

            self.switch_decryption_section(1)  # Show results section

        except ValueError as ve:  # Catch errors from backend (e.g., wrong password, corrupted data, image issues)
            QMessageBox.critical(self, "Decryption Error", f"Decryption failed: {ve}")
            self._clear_decryption_results()
        except Exception as e:  # Catch other unexpected errors
            QMessageBox.critical(self, "Extraction Error",
                                 f"An unexpected error occurred during extraction or decryption: {e}")
            self._clear_decryption_results()

    def _handle_result_action(self):
        """Routes the action button click based on content type (copy text or save file)."""
        if self.decrypted_is_text:
            self._copy_decrypted_text()
        else:
            self._download_decrypted_file()

    def _copy_decrypted_text(self):
        """Copies the decrypted text to the clipboard."""
        if self.decrypted_is_text and self.decrypted_raw_data:
            try:
                # Ensure it's decoded to a string for clipboard
                text_to_copy = self.decrypted_raw_data
                clipboard = QApplication.clipboard()
                clipboard.setText(text_to_copy)
                QMessageBox.information(self, "Copied", "Decrypted text copied to clipboard!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not copy text: {e}")
        else:
            QMessageBox.warning(self, "No Text", "No decrypted text available to copy.")

    def _download_decrypted_file(self):
        """Saves the decrypted file content to a user-specified location."""
        if not self.decrypted_is_text and self.decrypted_raw_data:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted File", self.suggested_filename,
                                                       "All Files (*.*)")

            if save_path:
                try:
                    with open(save_path, 'wb') as f:
                        f.write(self.decrypted_raw_data)
                    QMessageBox.information(self, "Download Complete", f"File saved successfully to:\n{save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Failed to save file: {e}")
            else:
                QMessageBox.warning(self, "Save Cancelled", "File download cancelled.")
        else:
            QMessageBox.warning(self, "No File", "No decrypted file available to download.")

    def _clear_decryption_results(self):
        """Clears the decryption results and resets UI for next decryption."""
        self.decrypted_raw_data = None
        self.decrypted_is_text = False
        self.decrypted_text_edit.clear()
        self.decrypted_text_edit.setPlaceholderText("Decrypted content will appear here...")
        self.result_action_btn.setText("Action Button")  # Reset button text to default (or hide it initially)
        self.suggested_filename = "extracted_content"  # Reset suggested filename

