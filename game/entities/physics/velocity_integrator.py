"""Integrate entity velocity into position."""

from __future__ import annotations

from .base import EntityPhysicsContext


class VelocityIntegrator:
    """Integrate velocity into position."""

    def process(self, context: EntityPhysicsContext) -> EntityPhysicsContext:
        state = context.state
        state.x += state.vx * context.dt
        state.y += state.vy * context.dt
        return context
