"""Processors for handling Mario power-up transitions."""

from __future__ import annotations

from .base import PhysicsContext, PhysicsProcessor


class MarioTransitionProcessor(PhysicsProcessor):
    """Manage mario's temporal transitions."""

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Update Mario's transition if one is in progress."""

        transition = context.mario.transition
        if transition is not None:
            transition.update(context.dt, context.mario)

        return context
