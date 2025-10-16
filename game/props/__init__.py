"""Prop system for persistent world decorations."""

from .base import Prop
from .flagpole import FlagpoleProp
from .manager import PropManager

__all__ = ["Prop", "PropManager", "FlagpoleProp"]
