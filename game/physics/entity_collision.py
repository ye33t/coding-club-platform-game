"""Handle collision detection between Mario and entities."""

from pygame import Rect

from game.constants import TILE_SIZE

from .base import PhysicsContext, PhysicsProcessor
from .config import STOMP_VELOCITY_Y_SCALE
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

        # First pass: Check if Mario is about to stomp an enemy
        if mario_state.vy < 0 and not mario_state.on_ground:
            # Mario is falling - check if there's an enemy below

            # Create a rect below Mario to check for potential stomps
            stomp_check_rect = Rect(
                int(mario_state.x + MARIO_HORIZONTAL_MARGIN),
                int(mario_state.y - TILE_SIZE),
                int(mario_state.width - (MARIO_HORIZONTAL_MARGIN * 2)),
                TILE_SIZE,
            )

            for entity in context.entities:
                # Check if this entity can be stomped
                if entity.is_stompable:
                    entity_rect = entity.get_collision_bounds()

                    # Check if Mario is aligned to stomp this enemy
                    if stomp_check_rect.colliderect(entity_rect):
                        # Check if Mario would be in stomp position (above top third)
                        entity_top = entity_rect.y + entity_rect.height
                        stomp_threshold = entity_top - (entity_rect.height * 0.33)

                        if mario_state.y > stomp_threshold:
                            # Mario is about to stomp - activate stomp mode
                            mario_state.is_stomping = True
                            break

        # Second pass: Handle actual collisions
        for entity in context.entities:
            entity_rect = entity.get_collision_bounds()

            if not mario_rect.colliderect(entity_rect):
                continue

            response = entity.on_collide_mario(mario_state)
            if not response:
                continue

            # Apply bounce velocity if specified (e.g., from stomping enemies)
            if response.bounce_velocity is not None:
                # Apply bounce but scale it down for more controlled stomping
                # This prevents excessive bouncing and gives players better control
                mario_state.vy = response.bounce_velocity * STOMP_VELOCITY_Y_SCALE

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
        - Invincible: No effect
        """
        mario_state = context.mario_state

        if mario_state.is_invincible:
            return

        if mario_state.size == "small":
            context.event = DeathEvent()
        elif mario_state.size == "big":
            mario_state.shrink()
