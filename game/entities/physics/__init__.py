"""Shared physics pipeline for non-Mario entities."""

from .base import EntityPhysicsContext, EntityProcessor
from .gravity import GravityProcessor
from .ground_snap import GroundSnapProcessor
from .horizontal_velocity import HorizontalVelocityProcessor
from .pipeline import EntityPipeline
from .velocity_integrator import VelocityIntegrator
from .wall_bounce import WallBounceProcessor

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
