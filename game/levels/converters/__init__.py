"""Compound converter registry and type definitions."""

from typing import Callable, Dict, Optional

from .pipe import TilePlacement, convert_pipe

CONVERTERS: Dict[str, Callable[..., Optional[TilePlacement]]] = {
    "|": convert_pipe,
}

__all__ = ["CONVERTERS", "TilePlacement"]
