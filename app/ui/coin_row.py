from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QFont
from app.constants import (
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_POSITIVE, COLOR_NEGATIVE, COLOR_WATCH,
    COLOR_BG_ROW, COLOR_BG_ROW_ALT, COIN_ID_TO_SYMBOL,
)
from app.ui.sparkline import SparklineWidget
from app.analysis.tips import CoinAnalysis

_SIGNAL_COLORS = {
    "BUY":  ("#00C896", "rgba(0,200,150,0.15)"),
    "SELL": ("#E94560", "rgba(233,69,96,0.15)"),
    "HOLD": ("#8892A4", "rgba(136,146,164,0.12)"),
    "WATCH": ("#FFB74D", "rgba(255,183,77,0.15)"),
}


def _format_price(price: float) -> str:
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"


class CoinRow(QWidget):
    tip_toggle_requested = pyqtSignal(str)   # coin_id
    remove_requested     = pyqtSignal(str)   # coin_id

    def __init__(self, coin_id: str, parent=None):
        super().__init__(parent)
        self._coin_id = coin_id
        self._hovered = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Left: symbol + name
        left = QVBoxLayout()
        left.setSpacing(2)
        symbol = COIN_ID_TO_SYMBOL.get(self._coin_id, self._coin_id.upper())
        self._symbol_label = QLabel(symbol)
        self._symbol_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;"
        )
        self._name_label = QLabel(self._coin_id.capitalize())
        self._name_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 10px;"
        )
        left.addWidget(self._symbol_label)
        left.addWidget(self._name_label)

        # Center: price + change
        center = QVBoxLayout()
        center.setSpacing(2)
        center.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._price_label = QLabel("---")
        self._price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._price_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px; font-weight: bold;"
        )
        self._change_label = QLabel("---")
        self._change_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._change_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;"
        )
        center.addWidget(self._price_label)
        center.addWidget(self._change_label)

        # Signal badge
        self._signal_label = QLabel("---")
        self._signal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._signal_label.setFixedWidth(46)
        self._signal_label.setStyleSheet(
            "color: #8892A4; background: rgba(136,146,164,0.12);"
            "border-radius: 4px; font-size: 10px; font-weight: bold;"
            "padding: 2px 4px;"
        )

        # Sparkline
        self._sparkline = SparklineWidget(self)

        # Remove button
        self._remove_btn = QPushButton("×")
        self._remove_btn.setFixedSize(16, 16)
        self._remove_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            f"color: #444466; font-size: 14px; font-weight: bold; }}"
            "QPushButton:hover { color: #E94560; }"
        )
        self._remove_btn.clicked.connect(lambda: self.remove_requested.emit(self._coin_id))
        self._remove_btn.setVisible(False)

        layout.addLayout(left)
        layout.addLayout(center)
        layout.addStretch()
        layout.addWidget(self._signal_label)
        layout.addWidget(self._sparkline)
        layout.addWidget(self._remove_btn)

    def update_price(self, price: float, change_24h: float):
        self._price_label.setText(_format_price(price))
        sign = "+" if change_24h >= 0 else ""
        self._change_label.setText(f"{sign}{change_24h:.2f}%")
        color = COLOR_POSITIVE if change_24h >= 0 else COLOR_NEGATIVE
        self._change_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: bold;"
        )

    def update_sparkline(self, prices: list):
        self._sparkline.set_data(prices)

    def update_analysis(self, analysis: CoinAnalysis):
        signal = analysis.signal
        fg, bg = _SIGNAL_COLORS.get(signal, ("#8892A4", "rgba(136,146,164,0.12)"))
        self._signal_label.setText(signal)
        self._signal_label.setStyleSheet(
            f"color: {fg}; background: {bg}; border-radius: 4px;"
            "font-size: 10px; font-weight: bold; padding: 2px 4px;"
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(COLOR_BG_ROW_ALT if self._hovered else COLOR_BG_ROW)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 6, 6)
        painter.fillPath(path, bg)
        painter.end()

    def enterEvent(self, event):
        self._hovered = True
        self._remove_btn.setVisible(True)
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self._remove_btn.setVisible(False)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Don't toggle tip if clicking remove button area
            if not self._remove_btn.geometry().contains(event.pos()):
                self.tip_toggle_requested.emit(self._coin_id)
