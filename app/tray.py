from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QSize


def _make_tray_icon() -> QIcon:
    """Generate a simple ₿ icon programmatically (no image file needed)."""
    size = 64
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Background circle
    painter.setBrush(QColor("#E94560"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, size - 4, size - 4)
    # ₿ text
    font = QFont("Segoe UI", 28, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor("white"))
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "₿")
    painter.end()
    return QIcon(px)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, widget, parent=None):
        super().__init__(_make_tray_icon(), parent)
        self._widget = widget
        self.setToolTip("Crypto Widget")
        self._build_menu()
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: #1A1A2E;
                color: #EAEAEA;
                border: 1px solid #2A2A4A;
                border-radius: 6px;
                padding: 4px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
            QMenu::item { padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background: rgba(233,69,96,0.2); }
            QMenu::separator { background: #2A2A4A; height: 1px; margin: 4px 8px; }
        """)

        show_action = menu.addAction("📊  Mostrar widget")
        show_action.triggered.connect(self._show_widget)

        hide_action = menu.addAction("🙈  Ocultar widget")
        hide_action.triggered.connect(self._widget.hide)

        menu.addSeparator()

        quit_action = menu.addAction("✕  Salir")
        quit_action.triggered.connect(self._quit)

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_widget()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self._widget.isVisible():
                self._widget.hide()
            else:
                self._show_widget()

    def _show_widget(self):
        self._widget.show()
        self._widget.raise_()
        self._widget.activateWindow()

    def _quit(self):
        from PyQt6.QtWidgets import QApplication
        self.hide()
        QApplication.quit()
