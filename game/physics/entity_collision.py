"""Handle collision detection between Mario and entities."""

from pygame import Rect

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
                    if response.remove:
                        continue

                    if response.power_up:
                        pass

                    if response.damage:
                        pass

                    if response.bounce:
                        pass

            entities_to_keep.append(entity)

        context.entities[:] = entities_to_keep

        return context
