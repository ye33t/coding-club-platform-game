"""Handle collision detection between Mario and entities."""

from pygame import Rect

from .base import PhysicsContext, PhysicsProcessor
from .events import DeathEvent


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

        # Shrink Mario's collision box horizontally for more accurate collision
        MARIO_HORIZONTAL_MARGIN = 2  # Pixels to shrink on each side

        mario_rect = Rect(
            int(mario_state.x + MARIO_HORIZONTAL_MARGIN),
            int(mario_state.y),
            int(mario_state.width - (MARIO_HORIZONTAL_MARGIN * 2)),
            int(mario_state.height),
        )

        for entity in context.entities:
            entity_rect = entity.get_collision_bounds()

            if not mario_rect.colliderect(entity_rect):
                continue

            response = entity.on_collide_mario(mario_state)
            if not response:
                continue

            # Apply bounce velocity if specified (e.g., from stomping enemies)
            if response.bounce_velocity is not None:
                mario_state.vy = response.bounce_velocity

            if response.power_up_type is not None:
                self._apply_power_up(context, response.power_up_type)

            if response.damage:
                self._apply_damage(context)

            if response.remove:
                context.entities_to_remove.add(entity)

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

        mario_state.grow()

    def _apply_damage(self, context: PhysicsContext) -> None:
        """Apply damage to Mario based on his current state.

        - Small Mario: Dies
        - Big Mario: Shrinks to small
        - Invincible (during transition): No effect
        """
        mario_state = context.mario_state

        # Check if Mario is invincible (during a transition)
        if mario_state.is_invincible:
            return

        # Check Mario's size and apply appropriate damage
        if mario_state.size == "small":
            # Small Mario dies
            context.event = DeathEvent()
        elif mario_state.size == "big":
            # Big Mario shrinks
            mario_state.shrink()
