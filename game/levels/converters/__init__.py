"""Compound converter registry and type definitions."""

from typing import Callable, Dict, Optional

from .flagpole import convert_flagpole
from .pipe import TilePlacement, convert_pipe

CONVERTERS: Dict[str, Callable[..., Optional[TilePlacement]]] = {
    "|": convert_pipe,
    "F": convert_flagpole,
}

__all__ = ["CONVERTERS", "TilePlacement"]
