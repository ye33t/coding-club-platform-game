"""Palette scheme loading and color mapping utilities."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping, Optional, Tuple

import yaml  # type: ignore[import-untyped]

Color = Tuple[int, int, int]
CHANNELS: Tuple[str, ...] = ("primary", "secondary", "accent")

ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
PALETTE_PATH = ASSET_ROOT / "config" / "palettes.yaml"


@dataclass(frozen=True)
class PaletteScheme:
    """Resolved palette information for a scheme."""

    name: str
    background: Color
    families: Mapping[str, Mapping[str, Color]]


class PaletteLibrary:
    """Loads palette configuration and resolves color mappings."""

    def __init__(self) -> None:
        self._schemes: Dict[str, PaletteScheme] = {}
        self._default_scheme: Optional[str] = None
        self._base_family_colors: Dict[str, Dict[str, Color]] = {}
        self._active_scheme: Optional[str] = None
        self._loaded: bool = False
        self._mapping_cache: Dict[Tuple[str, str], Optional[Mapping[Color, Color]]] = {}
        self._version: int = 0

    # Public API -----------------------------------------------------------------
    def reload(self) -> None:
        """Reload palette configuration."""
        self._loaded = False
        self._schemes.clear()
        self._base_family_colors.clear()
        self._default_scheme = None
        self._active_scheme = None
        self._mapping_cache.clear()
        self._ensure_loaded()

    @property
    def default_scheme_name(self) -> str:
        """Return the configured default scheme name."""
        self._ensure_loaded()
        if self._default_scheme is None:
            raise RuntimeError("No default palette scheme configured")
        return self._default_scheme

    def get_scheme(self, scheme_name: Optional[str] = None) -> PaletteScheme:
        """Retrieve a palette scheme by name (default if None)."""
        self._ensure_loaded()
        if scheme_name is None:
            scheme_name = self.default_scheme_name
        scheme = self._schemes.get(scheme_name)
        if scheme is None:
            raise KeyError(f"Unknown palette scheme '{scheme_name}'")
        return scheme

    def background_color(self, scheme_name: Optional[str] = None) -> Color:
        """Get the background color for a palette scheme."""
        return self.get_scheme(scheme_name).background

    def color_map_for(
        self, scheme_name: Optional[str], family: str
    ) -> Optional[Mapping[Color, Color]]:
        """Return base->target color mapping for a family within a scheme."""
        self._ensure_loaded()
        scheme = self.get_scheme(scheme_name)
        key = (scheme.name, family)
        if key in self._mapping_cache:
            return self._mapping_cache[key]

        base_colors = self._base_family_colors.get(family)
        if not base_colors:
            self._mapping_cache[key] = None
            return None

        scheme_family = scheme.families.get(family)
        if not scheme_family:
            self._mapping_cache[key] = None
            return None

        mapping: Dict[Color, Color] = {}
        changed = False
        for channel, base_color in base_colors.items():
            target_color = scheme_family.get(channel) or base_color
            mapping[base_color] = target_color
            if target_color != base_color:
                changed = True

        result: Optional[Mapping[Color, Color]] = mapping if changed else None
        self._mapping_cache[key] = result
        return result

    # Active scheme helpers ------------------------------------------------------
    @property
    def active_scheme_name(self) -> Optional[str]:
        """Current scheme applied during rendering."""
        return self._active_scheme

    def set_active_scheme(self, scheme_name: Optional[str]) -> PaletteScheme:
        """Set the scheme currently in use for rendering."""
        scheme = self.get_scheme(scheme_name)
        self._active_scheme = scheme.name
        return scheme

    def clear_active_scheme(self) -> None:
        """Clear any active scheme selection."""
        self._active_scheme = None

    @contextmanager
    def activate(self, scheme_name: Optional[str]):
        """Context manager to temporarily activate a palette scheme."""

        previous = self._active_scheme
        scheme = self.set_active_scheme(scheme_name)
        try:
            yield scheme
        finally:
            if previous is None:
                self._active_scheme = None
            else:
                try:
                    self._active_scheme = self.get_scheme(previous).name
                except KeyError:
                    self._active_scheme = self.default_scheme_name

    @property
    def version(self) -> int:
        """Monotonically increasing palette configuration version."""
        self._ensure_loaded()
        return self._version

    # Internal helpers -----------------------------------------------------------
    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._load()
        self._loaded = True

    def _load(self) -> None:
        if not PALETTE_PATH.exists():
            raise FileNotFoundError(f"Palette config not found: {PALETTE_PATH}")

        with PALETTE_PATH.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)

        if not isinstance(data, dict):
            raise ValueError("Palette config root must be a mapping")

        version = data.get("version")
        if version != 1:
            raise ValueError(f"Unsupported palette config version: {version!r}")

        schemes_payload = data.get("schemes")
        if not isinstance(schemes_payload, dict) or not schemes_payload:
            raise ValueError("Palette config requires a non-empty 'schemes' mapping")

        parsed_schemes: Dict[str, PaletteScheme] = {}
        default_candidate: Optional[str] = None

        for scheme_name, scheme_data in schemes_payload.items():
            if not isinstance(scheme_name, str):
                raise ValueError("Palette scheme names must be strings")
            if not isinstance(scheme_data, dict):
                raise ValueError(f"Palette scheme '{scheme_name}' must be a mapping")

            default_flag = bool(scheme_data.get("default", False))
            background_value = scheme_data.get("background")
            if background_value is None:
                raise ValueError(
                    f"Palette scheme '{scheme_name}' missing 'background' color"
                )
            background = _parse_color(
                background_value,
                f"scheme '{scheme_name}' background",
            )

            families_payload = scheme_data.get("families", {})
            if not isinstance(families_payload, dict):
                raise ValueError(
                    f"Palette scheme '{scheme_name}' families must be a mapping"
                )

            scheme_families: Dict[str, Dict[str, Color]] = {}
            for family, family_payload in families_payload.items():
                if not isinstance(family, str):
                    raise ValueError("Palette family names must be strings")
                if family_payload is None:
                    continue
                if not isinstance(family_payload, dict):
                    raise ValueError(
                        f"Palette scheme '{scheme_name}' family '{family}' must be a mapping"
                    )

                channel_colors: Dict[str, Color] = {}
                for channel in CHANNELS:
                    if channel not in family_payload:
                        continue
                    raw_color = family_payload[channel]
                    if raw_color is None:
                        continue
                    channel_colors[channel] = _parse_color(
                        raw_color,
                        f"scheme '{scheme_name}' family '{family}' channel '{channel}'",
                    )

                if channel_colors:
                    scheme_families[family] = channel_colors

            parsed_schemes[scheme_name] = PaletteScheme(
                name=scheme_name,
                background=background,
                families=scheme_families,
            )

            if default_flag:
                if default_candidate is not None:
                    raise ValueError("Multiple palette schemes marked as default")
                default_candidate = scheme_name

        if default_candidate is None:
            default_candidate = next(iter(parsed_schemes.keys()))

        self._schemes = parsed_schemes
        self._default_scheme = default_candidate
        self._build_base_colors()
        self._version += 1

    def _build_base_colors(self) -> None:
        if self._default_scheme is None:
            raise RuntimeError("Palette configuration missing default scheme")
        default_scheme = self._schemes[self._default_scheme]
        base_colors: Dict[str, Dict[str, Color]] = {}

        for family, colors in default_scheme.families.items():
            missing = [channel for channel in CHANNELS if channel not in colors]
            if missing:
                raise ValueError(
                    f"Default scheme '{default_scheme.name}' family '{family}' "
                    f"missing channels: {', '.join(missing)}"
                )
            base_colors[family] = dict(colors)

        self._base_family_colors = base_colors
        self._mapping_cache.clear()


def _parse_color(value, context: str) -> Color:
    """Normalize a hex color value to an RGB tuple."""
    integer: Optional[int] = None
    if isinstance(value, int):
        integer = value
    elif isinstance(value, str):
        text = value.strip().lower()
        if text.startswith("#"):
            text = text[1:]
        if text.startswith("0x"):
            text = text[2:]
        if not text:
            raise ValueError(f"Empty color string for {context}")
        try:
            integer = int(text, 16)
        except ValueError as exc:
            raise ValueError(f"Invalid color '{value}' for {context}") from exc
    else:
        raise ValueError(
            f"Color value for {context} must be int or hex string, got {type(value)!r}"
        )

    if integer is None or integer < 0 or integer > 0xFFFFFF:
        raise ValueError(f"Color value out of range for {context}: {value!r}")

    red = (integer >> 16) & 0xFF
    green = (integer >> 8) & 0xFF
    blue = integer & 0xFF
    return (red, green, blue)


# Singleton instance used throughout the game.
palettes = PaletteLibrary()
