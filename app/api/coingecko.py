import requests
from app.constants import COINGECKO_BASE, PERIOD_DAYS

_session = requests.Session()
_session.headers.update({"User-Agent": "crypto-widget/1.0"})
_TIMEOUT = 10


def fetch_prices(coin_ids: list, currency: str = "usd") -> dict:
    """
    Returns: {"bitcoin": {"price": 65000.0, "change_24h": 2.3}, ...}
    """
    if not coin_ids:
        return {}
    try:
        resp = _session.get(
            f"{COINGECKO_BASE}/simple/price",
            params={
                "ids": ",".join(coin_ids),
                "vs_currencies": currency,
                "include_24h_change": "true",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        result = {}
        for coin_id in coin_ids:
            if coin_id in data:
                entry = data[coin_id]
                result[coin_id] = {
                    "price": entry.get(currency, 0.0),
                    "change_24h": entry.get(f"{currency}_24h_change"),  # None if missing
                }
        return result
    except Exception as e:
        raise RuntimeError(f"fetch_prices failed: {e}") from e


def fetch_market_chart(coin_id: str, currency: str = "usd", days: int = 7) -> list:
    """
    Returns flat list of closing prices, chronological order.
    """
    try:
        params = {"vs_currency": currency, "days": days}
        if days >= 90:
            params["interval"] = "daily"
        resp = _session.get(
            f"{COINGECKO_BASE}/coins/{coin_id}/market_chart",
            params=params,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return [entry[1] for entry in data.get("prices", [])]
    except Exception as e:
        raise RuntimeError(f"fetch_market_chart failed: {e}") from e


def fetch_coin_list() -> list:
    """
    Returns: [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}, ...]
    """
    try:
        resp = _session.get(
            f"{COINGECKO_BASE}/coins/list",
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise RuntimeError(f"fetch_coin_list failed: {e}") from e
