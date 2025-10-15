"""Shared physics pipeline for non-Mario entities."""

from .base import EntityPhysicsContext, EntityProcessor
from .pipeline import EntityPipeline
from .processors import (
    GravityProcessor,
    GroundSnapProcessor,
    HorizontalVelocityProcessor,
    VelocityIntegrator,
    WallBounceProcessor,
)

__all__ = [
    "EntityPhysicsContext",
    "EntityProcessor",
    "EntityPipeline",
    "GravityProcessor",
    "GroundSnapProcessor",
    "HorizontalVelocityProcessor",
    "VelocityIntegrator",
    "WallBounceProcessor",
]
