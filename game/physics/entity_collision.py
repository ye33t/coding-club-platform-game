"""Handle collision detection between Mario and entities."""

from pygame import Rect

from ..constants import TILE_SIZE
from .base import PhysicsContext, PhysicsProcessor


class EntityCollisionProcessor(PhysicsProcessor):
    """Detects and handles collisions between Mario and entities.

    This processor:
    - Checks AABB collision between Mario and each entity
    - Calls entity's on_collide_mario() method
    - Handles collision responses (power-up, damage, etc.)
    - Removes entities marked for removal
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check for collisions between Mario and entities.

        Args:
            context: Physics context containing Mario state and entities

        Returns:
            Modified context with collision responses applied
        """
        mario_state = context.mario_state
        mario_rect = Rect(
            int(mario_state.x),
            int(mario_state.y),
            int(mario_state.width),
            int(mario_state.height),
        )

        entities_to_keep = []

        for entity in context.entities:
            entity_rect = entity.get_collision_bounds()

            if mario_rect.colliderect(entity_rect):
                response = entity.on_collide_mario(mario_state)

                if response:
                    if response.power_up_type != None:
                        self._apply_power_up(context, response.power_up_type)

                    if response.damage:
                        pass

                    if response.remove:
                        continue

            entities_to_keep.append(entity)

        context.entities[:] = entities_to_keep

        return context

    def _apply_power_up(
        self, context: PhysicsContext, power_up_type: str | None
    ) -> None:
        """Apply a power-up effect to Mario based on collision response."""
        if power_up_type == "mushroom":
            self._apply_mushroom(context)

    def _apply_mushroom(self, context: PhysicsContext) -> None:
        """Handle mushroom collection: grow Mario to big size."""
        mario_state = context.mario_state

        if mario_state.size == "big":
            return

        mario_state.size = "big"
        mario_state.width = TILE_SIZE
        mario_state.height = TILE_SIZE * 2
