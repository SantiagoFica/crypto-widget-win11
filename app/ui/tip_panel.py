from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSlot
)
from PyQt6.QtGui import QPainter, QColor, QPainterPath
from app.constants import COLOR_BG_ROW_ALT, COLOR_ACCENT, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY
from app.analysis.tips import CoinAnalysis

_SIGNAL_COLORS = {
    "BUY":   "#00C896",
    "SELL":  "#E94560",
    "HOLD":  "#8892A4",
    "WATCH": "#FFB74D",
}


class TipPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._expanded = False
        self._analysis: CoinAnalysis | None = None

        self.setMaximumHeight(0)
        self.setMinimumHeight(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 12, 10)
        layout.setSpacing(4)

        # Header: signal badge + period change
        header = QHBoxLayout()
        self._signal_label = QLabel()
        self._signal_label.setStyleSheet(
            "font-size: 12px; font-weight: bold; padding: 2px 8px;"
            "border-radius: 4px;"
        )
        self._meta_label = QLabel()
        self._meta_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 10px;"
        )
        header.addWidget(self._signal_label)
        header.addStretch()
        header.addWidget(self._meta_label)
        layout.addLayout(header)

        # Tip text
        self._tip_label = QLabel()
        self._tip_label.setWordWrap(True)
        self._tip_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 11px; line-height: 1.4;"
        )
        layout.addWidget(self._tip_label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(COLOR_BG_ROW_ALT)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 0, 0)
        painter.fillPath(path, bg)
        # Left accent bar
        painter.fillRect(0, 0, 3, self.height(), QColor(COLOR_ACCENT))
        painter.end()

    def show_analysis(self, analysis: CoinAnalysis):
        self._analysis = analysis
        signal = analysis.signal
        color = _SIGNAL_COLORS.get(signal, "#8892A4")
        self._signal_label.setText(f"  {signal}  ")
        self._signal_label.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: bold;"
            f"padding: 2px 8px; border-radius: 4px;"
            f"background: rgba(0,0,0,0.25); border: 1px solid {color};"
        )
        sign = "+" if analysis.change_period >= 0 else ""
        self._meta_label.setText(
            f"{analysis.period}: {sign}{analysis.change_period:.1f}%  |  "
            f"Vol: {analysis.volatility:.1f}%"
        )
        self._tip_label.setText(f"💡 {analysis.tip}")
        self._open()

    def hide_panel(self):
        if self._expanded:
            self._close()

    def toggle(self, analysis: CoinAnalysis):
        if self._expanded and self._analysis and self._analysis.coin_id == analysis.coin_id:
            self._close()
        else:
            self.show_analysis(analysis)

    def _open(self):
        self._expanded = True
        self.adjustSize()
        target = self.sizeHint().height() + 4
        anim = QPropertyAnimation(self, b"maximumHeight", self)
        anim.setDuration(180)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self.maximumHeight())
        anim.setEndValue(max(target, 80))
        anim.start()

    def _close(self):
        self._expanded = False
        anim = QPropertyAnimation(self, b"maximumHeight", self)
        anim.setDuration(150)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.setStartValue(self.maximumHeight())
        anim.setEndValue(0)
        anim.start()
