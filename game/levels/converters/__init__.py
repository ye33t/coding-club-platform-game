"""Compound converter registry and type definitions."""

from typing import TYPE_CHECKING, Callable, Dict, Optional, Tuple

# Type aliases
TilePlacement = Dict[Tuple[int, int], int]  # Maps (x, y) -> tile_id

if TYPE_CHECKING:
    from ..types import Compound, ParserContext
    ConverterFunc = Callable[[Compound, ParserContext], Optional[TilePlacement]]

# Import converter functions (delayed to avoid circular imports)
from .pipe import convert_pipe

# Converter registry
CONVERTERS: Dict[str, Callable] = {
    "|": convert_pipe,
}

__all__ = ["CONVERTERS", "TilePlacement"]