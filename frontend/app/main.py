import sys
from PyQt6.QtWidgets import QApplication, QLineEdit, QWidget, QLabel, QPushButton, QVBoxLayout, QMainWindow, QDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("League Live Game Connector")
        self.resize(300, 400)

        layout = QVBoxLayout()

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def on_connect(self):
        print("Clicked")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()