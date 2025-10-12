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
        mario = context.mario

        # Shrink Mario's collision box horizontally for more accurate collision
        MARIO_HORIZONTAL_MARGIN = 2  # Pixels to shrink on each side

        mario_rect = Rect(
            int(mario.x + MARIO_HORIZONTAL_MARGIN),
            int(mario.y),
            int(mario.width - (MARIO_HORIZONTAL_MARGIN * 2)),
            int(mario.height),
        )

        # First pass: Check if Mario is about to stomp an enemy
        if mario.vy < 0 and not mario.on_ground:
            # Mario is falling - check if there's an enemy below

            # Create a rect below Mario to check for potential stomps
            stomp_check_rect = Rect(
                int(mario.x + MARIO_HORIZONTAL_MARGIN),
                int(mario.y - TILE_SIZE),
                int(mario.width - (MARIO_HORIZONTAL_MARGIN * 2)),
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

                        if mario.y > stomp_threshold:
                            # Mario is about to stomp - activate stomp mode
                            mario.is_stomping = True
                            break

        # Second pass: Handle actual collisions
        for entity in context.entities:
            entity_rect = entity.get_collision_bounds()

            if not mario_rect.colliderect(entity_rect):
                continue

            response = entity.on_collide_mario(mario)
            if not response:
                continue

            # Apply bounce velocity if specified (e.g., from stomping enemies)
            if response.bounce_velocity is not None:
                # Apply bounce but scale it down for more controlled stomping
                # This prevents excessive bouncing and gives players better control
                mario.vy = response.bounce_velocity * STOMP_VELOCITY_Y_SCALE

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
        mario = context.mario

        mario.grow()

    def _apply_damage(self, context: PhysicsContext) -> None:
        """Apply damage to Mario based on his current state.

        - Small Mario: Dies
        - Big Mario: Shrinks to small
        - Invincible: No effect
        """
        mario = context.mario

        if mario.is_invincible:
            return

        if mario.size == "small":
            context.event = DeathEvent()
        elif mario.size == "big":
            mario.shrink()
