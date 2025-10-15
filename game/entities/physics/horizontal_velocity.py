"""Horizontal velocity maintenance processor."""

from __future__ import annotations

from dataclasses import dataclass

from .base import EntityPhysicsContext


@dataclass(slots=True)
class HorizontalVelocityProcessor:
    """Maintain horizontal velocity based on facing direction."""

    speed: float

    def process(self, context: EntityPhysicsContext) -> EntityPhysicsContext:
        state = context.state
        state.vx = self.speed * state.direction
        return context
