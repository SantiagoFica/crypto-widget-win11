from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSlot
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QFont

from app.config import AppConfig
from app.constants import (
    COLOR_BG, COLOR_BG_ALPHA, COLOR_BORDER,
    CORNER_RADIUS, WINDOW_WIDTH_DEFAULT, COIN_ID_TO_SYMBOL,
)
from app.api.worker import FetcherThread
from app.analysis.tips import analyze_coin, CoinAnalysis
from app.ui.title_bar import TitleBar
from app.ui.period_selector import PeriodSelector
from app.ui.coin_row import CoinRow
from app.ui.tip_panel import TipPanel
from app.ui.settings_dialog import SettingsDialog


class CryptoWidget(QWidget):
    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self._drag_pos: QPoint | None = None
        self._coin_rows: dict = {}        # coin_id -> CoinRow
        self._tip_panels: dict = {}       # coin_id -> TipPanel
        self._analyses: dict = {}         # coin_id -> CoinAnalysis
        self._prices: dict = {}           # coin_id -> {price, change_24h}
        self._histories: dict = {}        # coin_id -> [prices]
        self._active_tip: str | None = None
        self._current_period = config.default_period

        self._setup_window()
        self._build_ui()
        self._setup_worker()
        self._setup_timer()
        QTimer.singleShot(300, self._trigger_fetch)

    # ── Window setup ──────────────────────────────────────────────────────

    def _setup_window(self):
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        if self._config.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(self._config.opacity)
        self.setFixedWidth(self._config.window_width or WINDOW_WIDTH_DEFAULT)

        # Position
        pos = self._config.position
        if pos.get("x", -1) >= 0:
            self.move(pos["x"], pos["y"])
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            self.move(screen.right() - self.width() - 20, screen.top() + 40)

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(0)

        # Inner container (painted with rounded rect in paintEvent)
        self._container = QWidget(self)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Title bar
        self._title_bar = TitleBar(self._container)
        self._title_bar.close_requested.connect(self.close)
        self._title_bar.settings_requested.connect(self._open_settings)
        self._title_bar.pin_toggled.connect(self._toggle_on_top)
        container_layout.addWidget(self._title_bar)

        # Period selector
        self._period_selector = PeriodSelector(self._current_period, self._container)
        self._period_selector.setContentsMargins(10, 4, 10, 4)
        self._period_selector.period_changed.connect(self._on_period_changed)
        container_layout.addWidget(self._period_selector)

        # Scroll area for coin rows
        scroll = QScrollArea(self._container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:vertical { background: transparent; width: 4px; }"
            "QScrollBar::handle:vertical { background: rgba(255,255,255,0.2);"
            "border-radius: 2px; min-height: 20px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )

        self._rows_container = QWidget()
        self._rows_container.setStyleSheet("background: transparent;")
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(8, 4, 8, 8)
        self._rows_layout.setSpacing(3)

        scroll.setWidget(self._rows_container)
        scroll.setMaximumHeight(520)
        container_layout.addWidget(scroll)
        outer.addWidget(self._container)

        # Build initial rows
        self._rebuild_rows()

    def _rebuild_rows(self):
        # Clear existing
        for coin_id in list(self._coin_rows.keys()):
            self._remove_row(coin_id)

        for coin_id in self._config.coins:
            self._add_row(coin_id)

    def _add_row(self, coin_id: str):
        if coin_id in self._coin_rows:
            return

        row = CoinRow(coin_id, self._rows_container)
        row.tip_toggle_requested.connect(self._on_tip_toggle)
        row.remove_requested.connect(self._on_remove_coin)

        tip = TipPanel(self._rows_container)

        self._rows_layout.addWidget(row)
        self._rows_layout.addWidget(tip)
        self._coin_rows[coin_id] = row
        self._tip_panels[coin_id] = tip

        # Restore cached data if available
        if coin_id in self._prices:
            p = self._prices[coin_id]
            row.update_price(p["price"], p["change_24h"])
        if coin_id in self._histories:
            row.update_sparkline(self._histories[coin_id])
        if coin_id in self._analyses:
            row.update_analysis(self._analyses[coin_id])

    def _remove_row(self, coin_id: str):
        if coin_id in self._tip_panels:
            self._rows_layout.removeWidget(self._tip_panels[coin_id])
            self._tip_panels[coin_id].deleteLater()
            del self._tip_panels[coin_id]
        if coin_id in self._coin_rows:
            self._rows_layout.removeWidget(self._coin_rows[coin_id])
            self._coin_rows[coin_id].deleteLater()
            del self._coin_rows[coin_id]

    # ── Worker / timer ────────────────────────────────────────────────────

    def _setup_worker(self):
        self._worker = FetcherThread(self)
        self._worker.prices_ready.connect(self._on_prices_ready)
        self._worker.history_ready.connect(self._on_history_ready)
        self._worker.error_occurred.connect(self._on_fetch_error)
        self._worker.fetch_complete.connect(self._on_fetch_complete)
        self._worker.start()

    def _setup_timer(self):
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._trigger_fetch)
        self._refresh_timer.start(self._config.refresh_interval_seconds * 1000)

        self._countdown = self._config.refresh_interval_seconds
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._tick_countdown)
        self._countdown_timer.start(1000)

    def _trigger_fetch(self):
        self._countdown = self._config.refresh_interval_seconds
        self._title_bar.set_status("Actualizando...")
        periods = {cid: self._current_period for cid in self._config.coins}
        self._worker.configure(self._config.coins, periods, self._config.currency)
        self._worker.trigger_fetch()

    def _tick_countdown(self):
        self._countdown = max(0, self._countdown - 1)
        if self._countdown > 0:
            self._title_bar.set_status(f"↻ en {self._countdown}s")

    # ── Worker slots ──────────────────────────────────────────────────────

    @pyqtSlot(dict)
    def _on_prices_ready(self, data: dict):
        self._prices.update(data)
        for coin_id, info in data.items():
            if coin_id in self._coin_rows:
                self._coin_rows[coin_id].update_price(
                    info["price"], info["change_24h"]
                )

    @pyqtSlot(str, str, list)
    def _on_history_ready(self, coin_id: str, period: str, prices: list):
        self._histories[coin_id] = prices
        price_info = self._prices.get(coin_id, {})
        analysis = analyze_coin(
            coin_id,
            price_info.get("price", 0.0),
            price_info.get("change_24h", 0.0),
            prices,
            period,
        )
        self._analyses[coin_id] = analysis

        if coin_id in self._coin_rows:
            self._coin_rows[coin_id].update_sparkline(prices)
            self._coin_rows[coin_id].update_analysis(analysis)

        # Refresh tip panel if open
        if self._active_tip == coin_id and coin_id in self._tip_panels:
            self._tip_panels[coin_id].show_analysis(analysis)

    @pyqtSlot(str)
    def _on_fetch_error(self, msg: str):
        self._title_bar.set_status("⚠ Error de red")

    @pyqtSlot()
    def _on_fetch_complete(self):
        now = datetime.now().strftime("%H:%M:%S")
        self._title_bar.set_status(f"✓ {now}")

    # ── User actions ──────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_period_changed(self, period: str):
        self._current_period = period
        # Re-fetch history for all coins with new period
        periods = {cid: period for cid in self._config.coins}
        self._worker.configure(self._config.coins, periods, self._config.currency)
        for coin_id in self._config.coins:
            self._worker.trigger_period_fetch(coin_id, period)

    @pyqtSlot(str)
    def _on_tip_toggle(self, coin_id: str):
        analysis = self._analyses.get(coin_id)
        if not analysis:
            return

        # Close previous if different
        if self._active_tip and self._active_tip != coin_id:
            if self._active_tip in self._tip_panels:
                self._tip_panels[self._active_tip].hide_panel()

        panel = self._tip_panels.get(coin_id)
        if panel:
            panel.toggle(analysis)
            if self._active_tip == coin_id:
                self._active_tip = None
            else:
                self._active_tip = coin_id

    @pyqtSlot(str)
    def _on_remove_coin(self, coin_id: str):
        if len(self._config.coins) <= 1:
            return
        self._config.coins.remove(coin_id)
        self._config.save()
        if self._active_tip == coin_id:
            self._active_tip = None
        self._remove_row(coin_id)

    def _toggle_on_top(self, enabled: bool):
        self._config.always_on_top = enabled
        self._config.save()
        flags = self.windowFlags()
        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def _open_settings(self):
        dialog = SettingsDialog(self._config, self)
        dialog.settings_saved.connect(self._on_settings_saved)
        # Center on widget
        dialog.adjustSize()
        dialog.move(
            self.x() + (self.width() - dialog.width()) // 2,
            self.y() + 50,
        )
        dialog.exec()

    @pyqtSlot(object)
    def _on_settings_saved(self, config: AppConfig):
        self._config = config
        self.setWindowOpacity(config.opacity)
        self._refresh_timer.setInterval(config.refresh_interval_seconds * 1000)
        self._rebuild_rows()
        self._trigger_fetch()

    # ── Painting ──────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(COLOR_BG)
        bg.setAlpha(COLOR_BG_ALPHA)
        path = QPainterPath()
        path.addRoundedRect(
            6, 6, self.width() - 12, self.height() - 12,
            CORNER_RADIUS, CORNER_RADIUS
        )
        painter.fillPath(path, bg)
        # Border
        border = QColor(COLOR_BORDER)
        border.setAlpha(120)
        from PyQt6.QtGui import QPen
        painter.setPen(QPen(border, 1))
        painter.drawPath(path)
        painter.end()

    # ── Dragging ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._config.position = {"x": self.x(), "y": self.y()}
        self._config.save()
