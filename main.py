import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QHBoxLayout, QSpinBox, QGridLayout, QMessageBox, QFileDialog,
    QMenuBar, QMenu, QMainWindow, QFrame
)
from PySide6.QtGui import QIcon, QClipboard, QAction, QMouseEvent
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
import qdarktheme


class CustomTitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(48)
        self.setStyleSheet("background-color: #2c2c2c; color: white;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.title = QLabel("Cryptique", self)
        layout.addWidget(self.title)
        layout.addStretch()

        self.minimize_button = QPushButton("-", self)
        self.minimize_button.setFixedSize(30, 25)
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.minimize_button)

        self.close_button = QPushButton("×", self)
        self.close_button.setFixedSize(30, 25)
        self.close_button.clicked.connect(self.parent.close)
        layout.addWidget(self.close_button)

        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None


class CaesarCipherUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(500, 400)
        self.setWindowIcon(QIcon("logo.png"))

        self.themes = ["dark", "light"]
        self.current_theme_index = 0

        self.central = QWidget()
        self.main_layout = QVBoxLayout(self.central)
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)

        self.theme_button = QPushButton("Switch Theme")
        self.theme_button.setFixedWidth(200)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setText(f"Theme: {self.themes[self.current_theme_index].capitalize()}")
        self.theme_button.setStyleSheet("padding: 4px 10px; border-radius: 6px; margin: 6px auto;")
        self.main_layout.addWidget(self.theme_button, alignment=Qt.AlignCenter)
        
        self.tabs = QTabWidget()
        self.encrypt_tab = self.create_cipher_tab(is_encrypt=True)
        self.decrypt_tab = self.create_cipher_tab(is_encrypt=False)
        self.tabs.addTab(self.encrypt_tab, "Encrypt")
        self.tabs.addTab(self.decrypt_tab, "Decrypt")
        self.tabs.currentChanged.connect(self.focus_input_field)
        self.main_layout.addWidget(self.tabs)

        # Footer
        self.footer_label = QLabel('<a href="https://github.com/xHaMMaDy/">© 2025 Cryptique GUI - By HaMMaDy </a>')
        self.footer_label.setOpenExternalLinks(True)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("padding: 6px; font-size: 11px; color: gray;")

        self.footer_container = QHBoxLayout()
        self.footer_container.addStretch()
        self.footer_container.addWidget(self.footer_label)
        self.footer_container.addStretch()

        self.main_layout.addLayout(self.footer_container, stretch=1)

        self.animation = QPropertyAnimation(self.central, b"geometry")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.set_theme("dark")
        self.sync_titlebar_theme("dark")
        self.setCentralWidget(self.central)

    def toggle_theme(self):
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        theme = self.themes[self.current_theme_index]
        self.set_theme(theme)
        self.theme_button.setText(f"Theme: {theme.capitalize()}")
        start_rect = self.central.geometry()
        end_rect = QRect(start_rect.x(), start_rect.y(), start_rect.width(), start_rect.height())
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.start()
        theme = self.themes[self.current_theme_index]
        self.set_theme(theme)
        start_rect = self.central.geometry()
        end_rect = QRect(start_rect.x(), start_rect.y(), start_rect.width(), start_rect.height())
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.start()

    def set_theme(self, theme):
        QApplication.instance().setStyleSheet(qdarktheme.load_stylesheet(theme))
        self.sync_titlebar_theme(theme)

    def create_cipher_tab(self, is_encrypt=True):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        input_label = QLabel("Input Text")
        input_text = QPlainTextEdit()
        input_text.setPlaceholderText("Enter your text here...")
        input_text.setStyleSheet("font-size: 14px;")

        output_label = QLabel("Output Text")
        output_text = QPlainTextEdit()
        output_text.setReadOnly(True)
        output_text.setStyleSheet("font-size: 14px;")

        shift_layout = QHBoxLayout()
        shift_label = QLabel("Shift:")
        shift_spin = QSpinBox()
        shift_spin.setRange(1, 25)
        shift_spin.setValue(3)
        shift_layout.addWidget(shift_label)
        shift_layout.addWidget(shift_spin)
        shift_layout.addStretch()

        button_layout = QGridLayout()
        action_button = QPushButton("Encrypt" if is_encrypt else "Decrypt")
        clear_button = QPushButton("Clear")
        copy_button = QPushButton("Copy Output")
        save_button = QPushButton("Export")
        load_button = QPushButton("Import")

        action_button.clicked.connect(lambda: self.process_text(input_text, output_text, shift_spin.value(), is_encrypt))
        clear_button.clicked.connect(lambda: self.clear_fields(input_text, output_text))
        copy_button.clicked.connect(lambda: self.copy_output(output_text))
        save_button.clicked.connect(lambda: self.export_result(output_text))
        load_button.clicked.connect(lambda: self.import_input(input_text))

        button_layout.addWidget(action_button, 0, 0)
        button_layout.addWidget(clear_button, 0, 1)
        button_layout.addWidget(copy_button, 0, 2)
        button_layout.addWidget(save_button, 1, 0)
        button_layout.addWidget(load_button, 1, 1)

        layout.addWidget(input_label)
        layout.addWidget(input_text)
        layout.addLayout(shift_layout)
        layout.addWidget(output_label)
        layout.addWidget(output_text)
        layout.addLayout(button_layout)

        if is_encrypt:
            self.encrypt_input = input_text
            self.encrypt_output = output_text
            self.encrypt_shift = shift_spin
        else:
            self.decrypt_input = input_text
            self.decrypt_output = output_text
            self.decrypt_shift = shift_spin

        return widget

    def focus_input_field(self):
        if self.tabs.currentIndex() == 0:
            self.encrypt_input.setFocus()
        else:
            self.decrypt_input.setFocus()

    def process_text(self, input_widget, output_widget, shift, encrypt=True):
        text = input_widget.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Input text cannot be empty.")
            return
        shift = shift if encrypt else -shift
        result = self.caesar_cipher(text, shift)
        output_widget.setPlainText(result)

    def caesar_cipher(self, text, shift):
        result = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += char
        return result

    def clear_fields(self, input_widget, output_widget):
        input_widget.clear()
        output_widget.clear()

    def copy_output(self, output_widget):
        clipboard = QApplication.clipboard()
        clipboard.setText(output_widget.toPlainText())
        QMessageBox.information(self, "Copied", "Output copied to clipboard.")

    def export_result(self, output_widget):
        text = output_widget.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "There is no output to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Output", "output.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(text)

    def sync_titlebar_theme(self, theme):
        if theme == "light":
            self.title_bar.setStyleSheet("background-color: #f0f0f0; color: black;")
            self.footer_label.setStyleSheet("padding: 6px; font-size: 11px; color: #444444;")
        elif theme == "auto":
            self.title_bar.setStyleSheet("background-color: #d0d0d0; color: black;")
            self.footer_label.setStyleSheet("padding: 6px; font-size: 11px; color: #222222;")
        else:  # dark
            self.title_bar.setStyleSheet("background-color: #2c2c2c; color: white;")
            self.footer_label.setStyleSheet("padding: 6px; font-size: 11px; color: #bbbbbb;")

    def import_input(self, input_widget):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Input File", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'r') as f:
                input_widget.setPlainText(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(app.styleSheet() + """
        QMainWindow { border-radius: 15px; background-color: transparent; }
    """)
    window = CaesarCipherUI()
    window.setAttribute(Qt.WA_TranslucentBackground, True)
    window.show()
    sys.exit(app.exec())