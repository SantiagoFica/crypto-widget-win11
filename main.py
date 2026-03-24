import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from app.config import AppConfig
from app.ui.widget import CryptoWidget


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app.setFont(QFont("Segoe UI", 10))
    app.setQuitOnLastWindowClosed(True)

    config = AppConfig.load()
    widget = CryptoWidget(config)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
