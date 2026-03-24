from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QSlider, QSpinBox, QComboBox,
    QFrame, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPainterPath
from app.config import AppConfig
from app.constants import (
    KNOWN_COINS, COLOR_BG, COLOR_BG_ROW_ALT, COLOR_ACCENT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BORDER,
    MIN_REFRESH_SECONDS,
)

_DIALOG_STYLE = f"""
QDialog {{
    background: transparent;
}}
QLabel {{
    color: {COLOR_TEXT_PRIMARY};
    font-size: 12px;
}}
QListWidget {{
    background: {COLOR_BG_ROW_ALT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    color: {COLOR_TEXT_PRIMARY};
    font-size: 12px;
    padding: 4px;
}}
QListWidget::item:selected {{
    background: rgba(233,69,96,0.2);
    border-radius: 4px;
}}
QLineEdit {{
    background: {COLOR_BG_ROW_ALT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    color: {COLOR_TEXT_PRIMARY};
    padding: 4px 8px;
    font-size: 12px;
}}
QLineEdit:focus {{
    border: 1px solid {COLOR_ACCENT};
}}
QSpinBox, QComboBox {{
    background: {COLOR_BG_ROW_ALT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    color: {COLOR_TEXT_PRIMARY};
    padding: 4px 8px;
    font-size: 12px;
    min-height: 28px;
}}
QComboBox QAbstractItemView {{
    background: #1A1A2E;
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: rgba(233,69,96,0.2);
}}
QPushButton {{
    background: rgba(255,255,255,0.07);
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    color: {COLOR_TEXT_PRIMARY};
    padding: 6px 14px;
    font-size: 12px;
    min-height: 30px;
}}
QPushButton:hover {{
    background: rgba(255,255,255,0.12);
}}
#SaveButton {{
    background: rgba(233,69,96,0.2);
    border: 1px solid {COLOR_ACCENT};
    color: {COLOR_ACCENT};
    font-weight: bold;
}}
#SaveButton:hover {{
    background: rgba(233,69,96,0.35);
}}
QSlider::groove:horizontal {{
    background: {COLOR_BORDER};
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {COLOR_ACCENT};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {COLOR_ACCENT};
    border-radius: 2px;
}}
"""


class SettingsDialog(QDialog):
    settings_saved = pyqtSignal(object)   # AppConfig

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self._config = config
        self._available = {s: cid for s, cid in KNOWN_COINS.items()
                           if cid not in config.coins}

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(320)
        self.setStyleSheet(_DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        frame = QFrame()
        frame.setObjectName("SettingsFrame")
        frame.setStyleSheet(
            "QFrame#SettingsFrame { background: #12121C; border-radius: 12px;"
            f"border: 1px solid {COLOR_BORDER}; }}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        # Title
        title = QLabel("⚙  Configuración")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #4FC3F7;")
        layout.addWidget(title)

        self._add_separator(layout)

        # Coins section
        layout.addWidget(QLabel("Cryptomonedas activas:"))
        self._coin_list = QListWidget()
        self._coin_list.setMaximumHeight(120)
        self._coin_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        for coin_id in config.coins:
            from app.constants import COIN_ID_TO_SYMBOL
            symbol = COIN_ID_TO_SYMBOL.get(coin_id, coin_id.upper())
            self._coin_list.addItem(f"{symbol}  ({coin_id})")
        layout.addWidget(self._coin_list)

        # Add coin
        add_row = QHBoxLayout()
        self._add_combo = QComboBox()
        for symbol in sorted(self._available.keys()):
            self._add_combo.addItem(f"{symbol}", self._available[symbol])
        add_btn = QPushButton("+ Agregar")
        add_btn.clicked.connect(self._add_coin)
        remove_btn = QPushButton("− Quitar")
        remove_btn.clicked.connect(self._remove_coin)
        add_row.addWidget(self._add_combo, stretch=2)
        add_row.addWidget(add_btn)
        add_row.addWidget(remove_btn)
        layout.addLayout(add_row)

        self._add_separator(layout)

        # Refresh interval
        ref_row = QHBoxLayout()
        ref_row.addWidget(QLabel("Actualizar cada (segundos):"))
        self._refresh_spin = QSpinBox()
        self._refresh_spin.setRange(MIN_REFRESH_SECONDS, 3600)
        self._refresh_spin.setSingleStep(30)
        self._refresh_spin.setValue(config.refresh_interval_seconds)
        ref_row.addWidget(self._refresh_spin)
        layout.addLayout(ref_row)

        # Opacity
        op_row = QHBoxLayout()
        op_row.addWidget(QLabel("Opacidad:"))
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(50, 100)
        self._opacity_slider.setValue(int(config.opacity * 100))
        self._opacity_label = QLabel(f"{int(config.opacity * 100)}%")
        self._opacity_slider.valueChanged.connect(
            lambda v: self._opacity_label.setText(f"{v}%")
        )
        op_row.addWidget(self._opacity_slider)
        op_row.addWidget(self._opacity_label)
        layout.addLayout(op_row)

        self._add_separator(layout)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("SaveButton")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        outer.addWidget(frame)

    def _add_separator(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {COLOR_BORDER};")
        layout.addWidget(line)

    def _add_coin(self):
        idx = self._add_combo.currentIndex()
        if idx < 0:
            return
        symbol = self._add_combo.currentText().split()[0]
        coin_id = self._add_combo.itemData(idx)
        if coin_id not in self._get_current_ids():
            self._coin_list.addItem(f"{symbol}  ({coin_id})")
            self._add_combo.removeItem(idx)

    def _remove_coin(self):
        row = self._coin_list.currentRow()
        if row >= 0 and self._coin_list.count() > 1:
            item = self._coin_list.takeItem(row)
            # parse back to add_combo
            text = item.text()
            coin_id = text.split("(")[-1].rstrip(")")
            from app.constants import COIN_ID_TO_SYMBOL
            symbol = COIN_ID_TO_SYMBOL.get(coin_id, coin_id.upper())
            self._add_combo.addItem(f"{symbol}", coin_id)

    def _get_current_ids(self) -> list:
        ids = []
        for i in range(self._coin_list.count()):
            text = self._coin_list.item(i).text()
            coin_id = text.split("(")[-1].rstrip(")")
            ids.append(coin_id)
        return ids

    def _save(self):
        self._config.coins = self._get_current_ids()
        self._config.refresh_interval_seconds = self._refresh_spin.value()
        self._config.opacity = self._opacity_slider.value() / 100.0
        self._config.save()
        self.settings_saved.emit(self._config)
        self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        painter.end()
