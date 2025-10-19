"""Load gameplay configuration values used by the HUD and score systems."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, Mapping

CONFIG_PATH = Path(__file__).parent.parent / "assets" / "config" / "gameplay.toml"

try:
    with open(CONFIG_PATH, "rb") as config_file:
        _CONFIG = tomllib.load(config_file)
except FileNotFoundError as exc:
    raise FileNotFoundError(
        f"Gameplay config file not found: {CONFIG_PATH}\n"
        "The game requires gameplay.toml to run."
    ) from exc
except tomllib.TOMLDecodeError as exc:
    raise ValueError(
        f"Invalid TOML in gameplay config: {CONFIG_PATH}\nError: {exc}"
    ) from exc

try:
    _hud_config = _CONFIG["hud"]
except KeyError as exc:
    raise KeyError("Gameplay config missing required 'hud' section") from exc

try:
    _score_popup_config = _CONFIG["score_popups"]
except KeyError as exc:
    raise KeyError("Gameplay config missing required 'score_popups' section") from exc


def _get_int(config: Mapping[str, Any], key: str) -> int:
    value = config.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Gameplay config 'hud.{key}' must be an integer")
    return value


HUD_DEFAULT_TIMER_START = _get_int(_hud_config, "default_timer_start")
HUD_TIMER_FRAMES_PER_DECREMENT = _get_int(_hud_config, "timer_frames_per_decrement")
HUD_SCORE_DIGITS = _get_int(_hud_config, "score_digits")
HUD_COIN_DIGITS = _get_int(_hud_config, "coin_digits")
HUD_TIMER_DIGITS = _get_int(_hud_config, "timer_digits")
HUD_COIN_SCORE_VALUE = _get_int(_hud_config, "coin_score_value")
HUD_COIN_INCREMENT = _get_int(_hud_config, "coin_increment")


def _get_float(config: Mapping[str, Any], key: str) -> float:
    value = config.get(key)
    if isinstance(value, int):
        return float(value)
    if not isinstance(value, (float, int)):
        raise ValueError(f"Gameplay config 'score_popups.{key}' must be numeric")
    return float(value)


SCORE_POPUP_VERTICAL_OFFSET = _get_float(_score_popup_config, "vertical_offset")
SCORE_POPUP_UPWARD_SPEED = _get_float(_score_popup_config, "upward_speed")
SCORE_POPUP_LIFETIME_FRAMES = _get_int(_score_popup_config, "lifetime_frames")
