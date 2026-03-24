from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup
from PyQt6.QtCore import pyqtSignal
from app.constants import (
    PERIOD_BTN_WIDTH, PERIOD_BTN_HEIGHT,
    COLOR_ACCENT, COLOR_TEXT_SECONDARY, COLOR_BG_ROW_ALT,
)

PERIODS = ["1D", "7D", "30D", "90D", "1Y"]

_STYLE = f"""
QPushButton {{
    background: transparent;
    border: 1px solid #2A2A4A;
    border-radius: 4px;
    color: {COLOR_TEXT_SECONDARY};
    font-size: 11px;
    font-weight: 500;
    min-width: {PERIOD_BTN_WIDTH}px;
    max-width: {PERIOD_BTN_WIDTH}px;
    min-height: {PERIOD_BTN_HEIGHT}px;
    max-height: {PERIOD_BTN_HEIGHT}px;
}}
QPushButton:checked {{
    background: rgba(233, 69, 96, 0.2);
    border: 1px solid {COLOR_ACCENT};
    color: {COLOR_ACCENT};
    font-weight: bold;
}}
QPushButton:hover:!checked {{
    background: rgba(255, 255, 255, 0.06);
    color: #C0C8D4;
}}
"""


class PeriodSelector(QWidget):
    period_changed = pyqtSignal(str)

    def __init__(self, default_period: str = "7D", parent=None):
        super().__init__(parent)
        self._current = default_period
        self._buttons: dict = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        for period in PERIODS:
            btn = QPushButton(period)
            btn.setCheckable(True)
            btn.setChecked(period == default_period)
            btn.setStyleSheet(_STYLE)
            btn.clicked.connect(lambda _, p=period: self._on_click(p))
            self._group.addButton(btn)
            self._buttons[period] = btn
            layout.addWidget(btn)

        layout.addStretch()

    def _on_click(self, period: str):
        if period != self._current:
            self._current = period
            self.period_changed.emit(period)

    def set_period(self, period: str):
        self._current = period
        if period in self._buttons:
            self._buttons[period].setChecked(True)

    def current_period(self) -> str:
        return self._current
