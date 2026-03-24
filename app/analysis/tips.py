import math
from dataclasses import dataclass
from app.constants import (
    TIP_STRONG_BULL_PCT, TIP_BULL_PCT,
    TIP_BEAR_PCT, TIP_STRONG_BEAR_PCT,
    TIP_HIGH_VOLATILITY, COIN_ID_TO_SYMBOL,
)


@dataclass
class CoinAnalysis:
    coin_id: str
    symbol: str
    current_price: float
    change_24h: float
    change_period: float
    volatility: float       # % avg daily std dev
    trend: str              # "bullish" | "bearish" | "sideways"
    signal: str             # "BUY" | "SELL" | "HOLD" | "WATCH"
    tip: str
    confidence: str         # "high" | "medium" | "low"
    period: str


def _linear_slope(values: list) -> float:
    """Returns slope of least-squares fit (positive = uptrend)."""
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den else 0.0


def _volatility(prices: list) -> float:
    """Returns coefficient of variation (%) of daily returns."""
    if len(prices) < 2:
        return 0.0
    returns = [
        abs((prices[i] - prices[i - 1]) / prices[i - 1] * 100)
        for i in range(1, len(prices))
    ]
    mean = sum(returns) / len(returns)
    return mean


def analyze_coin(
    coin_id: str,
    current_price: float,
    change_24h: float,
    history: list,
    period: str = "7D",
) -> CoinAnalysis:
    symbol = COIN_ID_TO_SYMBOL.get(coin_id, coin_id.upper())

    if len(history) < 3:
        return CoinAnalysis(
            coin_id=coin_id, symbol=symbol,
            current_price=current_price, change_24h=change_24h,
            change_period=0.0, volatility=0.0,
            trend="sideways", signal="WATCH",
            tip="Datos insuficientes para análisis.",
            confidence="low", period=period,
        )

    change_period = (history[-1] - history[0]) / history[0] * 100
    vol = _volatility(history)
    slope = _linear_slope(history)
    trend = "bullish" if slope > 0 else ("bearish" if slope < 0 else "sideways")

    confidence = "high" if len(history) >= 14 else "medium" if len(history) >= 7 else "low"

    period_labels = {
        "1D": "24h", "7D": "7 días", "30D": "30 días",
        "90D": "3 meses", "1Y": "1 año",
    }
    period_str = period_labels.get(period, period)

    # Determine signal
    if vol >= TIP_HIGH_VOLATILITY:
        signal = "WATCH"
    elif change_period >= TIP_STRONG_BULL_PCT and trend == "bullish":
        signal = "BUY"
    elif change_period >= TIP_BULL_PCT and trend == "bullish":
        signal = "BUY"
    elif change_period <= TIP_STRONG_BEAR_PCT and trend == "bearish":
        signal = "SELL"
    elif change_period <= TIP_BEAR_PCT and trend == "bearish":
        signal = "SELL"
    else:
        signal = "HOLD"

    # Build tip text
    tip_parts = []

    if signal == "BUY":
        if change_period >= TIP_STRONG_BULL_PCT:
            tip_parts.append(
                f"Subió {change_period:.1f}% en {period_str} con momentum alcista fuerte."
            )
            tip_parts.append("Considera tomar ganancias parciales si ya estás invertido.")
        else:
            tip_parts.append(f"Tendencia positiva: +{change_period:.1f}% en {period_str}.")
            tip_parts.append("Momento favorable para entrada escalonada.")
    elif signal == "SELL":
        if change_period <= TIP_STRONG_BEAR_PCT:
            tip_parts.append(
                f"Caída de {abs(change_period):.1f}% en {period_str}. Tendencia bajista persistente."
            )
            tip_parts.append("Posible oportunidad a largo plazo, pero espera confirmación de rebote.")
        else:
            tip_parts.append(f"Caída de {abs(change_period):.1f}% en {period_str}.")
            tip_parts.append("Espera señales de reversión antes de entrar.")
    elif signal == "WATCH":
        tip_parts.append(
            f"Alta volatilidad ({vol:.1f}% promedio diario). Riesgo elevado."
        )
        tip_parts.append("Usar stop-loss y no superar el 5% del portafolio.")
    else:  # HOLD
        tip_parts.append(f"Precio lateral ({change_period:+.1f}% en {period_str}).")
        tip_parts.append("Sin señal clara. Espera ruptura de rango para actuar.")

    # Append 24h context
    if abs(change_24h) >= 3:
        direction = "subió" if change_24h > 0 else "cayó"
        tip_parts.append(f"En las últimas 24h {direction} {abs(change_24h):.1f}%.")

    tip = " ".join(tip_parts)

    return CoinAnalysis(
        coin_id=coin_id, symbol=symbol,
        current_price=current_price, change_24h=change_24h,
        change_period=change_period, volatility=vol,
        trend=trend, signal=signal,
        tip=tip, confidence=confidence, period=period,
    )
