import sys
import requests
from PyQt6.QtWidgets import QApplication, QLineEdit, QWidget, QLabel, QPushButton, QVBoxLayout, QMainWindow
from PyQt6.QtCore import QTimer

from config import LEAGUE_LIVE_API, BACKEND_API
from utils import league_live_api, send_to_backend


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Runtime Variables
        self.is_connected = False
        self.is_streaming = False
        self.player_username = ""
        self.secret_token = ""

        self.api_timer = QTimer()
        self.api_timer.timeout.connect(self.call_api)
        self.api_timer.setInterval(2000)

        self.setWindowTitle("League Live Game Connector")
        self.resize(300, 400)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Live Game Stream"))

        self.notification_label = QLabel("")
        self.notification_label.setWordWrap(True)
        self.notification_label.setMinimumHeight(40)
        self.notification_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                border-radius: 4px;
                font-size: 12px;
                background-color: transparent;
            }
        """)
        self.notification_label.hide()
        layout.addWidget(self.notification_label)
        layout.addSpacing(5)

        username_label = QLabel("League Username:")
        username_label.setStyleSheet("margin-bottom: 0px; font-weight: bold;")
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your League username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        layout.addWidget(self.username_input)

        token_label = QLabel("Secret Token:")
        token_label.setStyleSheet("margin-bottom: 0px; font-weight: bold;")
        layout.addWidget(token_label)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your secret token")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        layout.addWidget(self.token_input)
        layout.addSpacing(15)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.on_connect)
        self.connect_button.setMinimumHeight(40)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        layout.addWidget(self.connect_button)

        self.stream_button = QPushButton("Start Stream")
        self.stream_button.clicked.connect(self.toggle_stream)
        self.stream_button.setMinimumHeight(40)
        self.update_stream_button_style()
        layout.addWidget(self.stream_button)
        

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def show_notification(self, message, type="info"):
        self.notification_label.setText(message)
        self.notification_label.show()

        if type == "error":
            self.notification_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 12px;
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
            """)
        elif type == "warning":
            self.notification_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 12px;
                    background-color: #fff3cd;
                    color: #856404;
                    border: 1px solid #ffeaa7;
                }
            """)
        elif type == "success":
            self.notification_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 12px;
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
            """)
        else:
            self.notification_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 12px;
                    background-color: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                }
            """)

    def hide_notification(self):
        self.notification_label.hide()

    def on_connect(self):
        self.player_username = self.username_input.text()
        self.secret_token = self.token_input.text()

        if not self.player_username or not self.secret_token:
            self.show_notification("Please enter both username and token", "error")
            return

        self.is_connected = True
        self.show_notification(f"Connected as {self.player_username}", "success")
        print(f"Connect clicked - Username: {self.player_username}, Token: {'*' * len(self.secret_token)}")

    def toggle_stream(self):
        if self.is_connected:
            self.is_streaming = not self.is_streaming

            if self.is_streaming:
                self.stream_button.setText("Stop Stream")
                self.api_timer.start()
                self.show_notification("Stream started - polling every 2 seconds", "info")
            else:
                self.stream_button.setText("Start Stream")
                self.api_timer.stop()
                self.show_notification("Stream stopped", "info")

            self.update_stream_button_style()
        else:
            self.show_notification("Please connect first before starting stream", "warning")

    def call_api(self):
        data = league_live_api()
        if (data.is_success()):
            send_to_backend(data.data)

    def update_stream_button_style(self):
        if self.is_streaming:
            self.stream_button.setStyleSheet("""
                QPushButton {
                    background-color: #d13438;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #b02a2e;
                }
                QPushButton:pressed {
                    background-color: #8e2124;
                }
            """)
        else:
            self.stream_button.setStyleSheet("""
                QPushButton {
                    background-color: #107c10;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #0e6b0e;
                }
                QPushButton:pressed {
                    background-color: #0c5a0c;
                }
            """)
        

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()