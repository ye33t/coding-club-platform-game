"""Physics processor that advances terrain behaviors."""

from .base import PhysicsContext, PhysicsProcessor


class TerrainBehaviorProcessor(PhysicsProcessor):
    """Advance terrain behaviors so they can emit physics events."""

    def process(self, context: PhysicsContext) -> PhysicsContext:
        context.level.terrain_manager.process_behaviors(context.dt, context)
        return context
