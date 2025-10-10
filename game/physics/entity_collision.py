"""Handle collision detection between Mario and entities."""

from pygame import Rect

from .base import PhysicsContext, PhysicsProcessor
from .config import SMALL_TO_BIG_TRANSITION_DURATION


class EntityCollisionProcessor(PhysicsProcessor):
    """Detects and handles collisions between Mario and entities.

    This processor:
    - Checks AABB collision between Mario and each entity
    - Calls entity's on_collide_mario() method
    - Handles collision responses (power-up, damage, etc.)
    - Marks entities for removal when appropriate
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check for collisions between Mario and entities."""
        mario_state = context.mario_state
        mario_rect = Rect(
            int(mario_state.x),
            int(mario_state.y),
            int(mario_state.width),
            int(mario_state.height),
        )

        for entity in context.entities:
            entity_rect = entity.get_collision_bounds()

            if not mario_rect.colliderect(entity_rect):
                continue

            response = entity.on_collide_mario(mario_state)
            if not response:
                continue

            if response.power_up_type is not None:
                self._apply_power_up(context, response.power_up_type)

            if response.damage:
                pass

            if response.remove:
                context.entities_to_remove.append(entity)

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

        original_size = mario_state.size
        mario_state.transition_from_size = original_size
        mario_state.transition_to_size = "big"
        mario_state.power_up_transition = "small_to_big"
        mario_state.transition_time_remaining = SMALL_TO_BIG_TRANSITION_DURATION
        mario_state.transition_toggle_counter = 0
        mario_state.transition_show_target = True
        mario_state.set_size("big")
