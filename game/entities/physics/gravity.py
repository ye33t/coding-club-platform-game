"""Gravity processor for entity physics."""

from __future__ import annotations

from dataclasses import dataclass

from .base import EntityPhysicsContext


@dataclass(slots=True)
class GravityProcessor:
    """Apply a constant downward acceleration."""

    gravity: float

    def process(self, context: EntityPhysicsContext) -> EntityPhysicsContext:
        state = context.state
        state.vy -= self.gravity * context.dt
        return context
