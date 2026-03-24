from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from app.constants import COLOR_TITLE, COLOR_TEXT_SECONDARY, COLOR_BG_ROW_ALT, COLOR_ACCENT

_BTN_STYLE = """
QPushButton {{
    background: transparent;
    border: none;
    color: {color};
    font-size: {size}px;
    min-width: 24px; max-width: 24px;
    min-height: 24px; max-height: 24px;
    border-radius: 4px;
    padding: 0px;
}}
QPushButton:hover {{
    background: {hover_bg};
}}
"""


class TitleBar(QWidget):
    close_requested    = pyqtSignal()
    settings_requested = pyqtSignal()
    pin_toggled        = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pinned = False
        self.setFixedHeight(38)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 8, 4)
        layout.setSpacing(6)

        # Title
        title = QLabel("₿ Crypto Widget")
        title.setStyleSheet(
            f"color: {COLOR_TITLE}; font-size: 13px; font-weight: bold;"
        )

        # Status
        self._status_label = QLabel("Iniciando...")
        self._status_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 10px;"
        )
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Pin button
        self._pin_btn = QPushButton("📌")
        self._pin_btn.setStyleSheet(
            _BTN_STYLE.format(color="#8892A4", size=13, hover_bg="rgba(255,255,255,0.08)")
        )
        self._pin_btn.setToolTip("Mantener encima de otras ventanas")
        self._pin_btn.clicked.connect(self._toggle_pin)

        # Settings button
        settings_btn = QPushButton("⚙")
        settings_btn.setStyleSheet(
            _BTN_STYLE.format(color="#8892A4", size=14, hover_bg="rgba(255,255,255,0.08)")
        )
        settings_btn.setToolTip("Configuración")
        settings_btn.clicked.connect(self.settings_requested)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet(
            _BTN_STYLE.format(color="#8892A4", size=13, hover_bg=f"rgba(233,69,96,0.25)")
        )
        close_btn.setToolTip("Cerrar")
        close_btn.clicked.connect(self.close_requested)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self._status_label)
        layout.addWidget(self._pin_btn)
        layout.addWidget(settings_btn)
        layout.addWidget(close_btn)

    def set_status(self, text: str):
        self._status_label.setText(text)

    def _toggle_pin(self):
        self._pinned = not self._pinned
        opacity = "1.0" if self._pinned else "0.5"
        color = COLOR_TITLE if self._pinned else "#8892A4"
        self._pin_btn.setStyleSheet(
            _BTN_STYLE.format(color=color, size=13, hover_bg="rgba(255,255,255,0.08)")
        )
        self.pin_toggled.emit(self._pinned)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(COLOR_BG_ROW_ALT)
        bg.setAlpha(80)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        painter.fillPath(path, bg)
        painter.end()
