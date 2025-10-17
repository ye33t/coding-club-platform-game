"""Compound converter registry and type definitions."""

from typing import Callable, Dict, Optional

from .bush import convert_bush
from .castle import convert_castle
from .cloud import convert_cloud
from .flagpole import convert_flagpole
from .pipe import TilePlacement, convert_pipe

CONVERTERS: Dict[str, Callable[..., Optional[TilePlacement]]] = {
    "|": convert_pipe,
    "F": convert_flagpole,
    "B": convert_bush,
    "C": convert_cloud,
    "K": convert_castle,
}

__all__ = ["CONVERTERS", "TilePlacement"]
