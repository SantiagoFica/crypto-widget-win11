from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from app.constants import PERIOD_DAYS
from app import api as _api_pkg  # avoid circular; we import coingecko inside run
import app.api.coingecko as coingecko


class DataFetcher(QObject):
    """Lives inside FetcherThread. All network calls happen here."""

    prices_ready   = pyqtSignal(dict)        # {coin_id: {price, change_24h}}
    history_ready  = pyqtSignal(str, str, list)  # (coin_id, period, [prices])
    error_occurred = pyqtSignal(str)
    fetch_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._coins: list = []
        self._periods: dict = {}   # coin_id -> period string
        self._currency: str = "usd"

    def configure(self, coins: list, periods: dict, currency: str = "usd"):
        """Called from main thread before fetching."""
        self._coins = list(coins)
        self._periods = dict(periods)
        self._currency = currency

    @pyqtSlot()
    def run_fetch(self):
        """Triggered by QTimer in main thread via queued connection."""
        if not self._coins:
            self.fetch_complete.emit()
            return

        # 1. Fetch current prices
        try:
            prices = coingecko.fetch_prices(self._coins, self._currency)
            self.prices_ready.emit(prices)
        except Exception as e:
            self.error_occurred.emit(str(e))
            prices = {}

        # 2. Fetch history per coin
        for coin_id in self._coins:
            period = self._periods.get(coin_id, "7D")
            days = PERIOD_DAYS.get(period, 7)
            try:
                history = coingecko.fetch_market_chart(coin_id, self._currency, days)
                self.history_ready.emit(coin_id, period, history)
            except Exception as e:
                self.error_occurred.emit(f"{coin_id}: {e}")

        self.fetch_complete.emit()

    @pyqtSlot(str, str)
    def fetch_single_period(self, coin_id: str, period: str):
        """Triggered when user changes the period for one coin."""
        days = PERIOD_DAYS.get(period, 7)
        try:
            history = coingecko.fetch_market_chart(coin_id, self._currency, days)
            self.history_ready.emit(coin_id, period, history)
        except Exception as e:
            self.error_occurred.emit(f"{coin_id}: {e}")


class FetcherThread(QThread):
    """Owns the event loop for DataFetcher."""

    # Proxy signals so widget can connect directly to FetcherThread
    prices_ready   = pyqtSignal(dict)
    history_ready  = pyqtSignal(str, str, list)
    error_occurred = pyqtSignal(str)
    fetch_complete = pyqtSignal()

    # Trigger signals (main thread -> worker thread)
    _trigger_fetch         = pyqtSignal()
    _trigger_period_fetch  = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fetcher: DataFetcher | None = None

    def run(self):
        self._fetcher = DataFetcher()

        # Connect worker signals to proxy signals (queued by default across threads)
        self._fetcher.prices_ready.connect(self.prices_ready)
        self._fetcher.history_ready.connect(self.history_ready)
        self._fetcher.error_occurred.connect(self.error_occurred)
        self._fetcher.fetch_complete.connect(self.fetch_complete)

        # Connect trigger signals to worker slots (queued connection)
        self._trigger_fetch.connect(self._fetcher.run_fetch)
        self._trigger_period_fetch.connect(self._fetcher.fetch_single_period)

        self.exec()  # start this thread's event loop

    def configure(self, coins: list, periods: dict, currency: str = "usd"):
        """Must be called before trigger_fetch."""
        if self._fetcher:
            self._fetcher.configure(coins, periods, currency)

    def trigger_fetch(self):
        self._trigger_fetch.emit()

    def trigger_period_fetch(self, coin_id: str, period: str):
        self._trigger_period_fetch.emit(coin_id, period)
