import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

DEFAULTS = {
    "coins": ["bitcoin", "ethereum", "solana"],
    "currency": "usd",
    "refresh_interval_seconds": 60,
    "always_on_top": False,
    "opacity": 0.95,
    "position": {"x": -1, "y": -1},
    "default_period": "7D",
    "window_width": 360,
}


@dataclass
class AppConfig:
    coins: list = field(default_factory=lambda: list(DEFAULTS["coins"]))
    currency: str = DEFAULTS["currency"]
    refresh_interval_seconds: int = DEFAULTS["refresh_interval_seconds"]
    always_on_top: bool = DEFAULTS["always_on_top"]
    opacity: float = DEFAULTS["opacity"]
    position: dict = field(default_factory=lambda: dict(DEFAULTS["position"]))
    default_period: str = DEFAULTS["default_period"]
    window_width: int = DEFAULTS["window_width"]

    @classmethod
    def load(cls) -> "AppConfig":
        data = dict(DEFAULTS)
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                data.update(saved)
            except Exception:
                pass
        return cls(**{k: data[k] for k in DEFAULTS})

    def save(self) -> None:
        tmp = CONFIG_PATH.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
            os.replace(tmp, CONFIG_PATH)
        except Exception:
            pass
