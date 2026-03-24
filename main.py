import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from app.config import AppConfig
from app.ui.widget import CryptoWidget
from app.tray import TrayIcon


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setQuitOnLastWindowClosed(False)  # keep alive via tray icon

    config = AppConfig.load()
    widget = CryptoWidget(config)

    tray = TrayIcon(widget)
    tray.show()

    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
