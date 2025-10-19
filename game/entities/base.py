"""Base classes for game entities (enemies and collectibles)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from pygame import Rect, Surface

from ..camera import Camera
from ..constants import TILE_SIZE
from ..rendering.base import Drawable
from .physics import EntityPhysicsContext, EntityPipeline

if TYPE_CHECKING:
    from ..level import Level
    from ..mario import Mario
    from ..score import ScoreType


@dataclass(slots=True)
class EntityState:
    """State for a game entity."""

    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    screen: int = 0
    width: float = TILE_SIZE
    height: float = TILE_SIZE
    facing_right: bool = False
    on_ground: bool = False


class CollisionResponse:
    """Response to collision with Mario."""

    def __init__(
        self,
        remove: bool = False,
        damage: bool = False,
        power_up_type: Optional[str] = None,
        bounce_velocity: Optional[float] = None,
        spawn_entity: Optional["Entity"] = None,
        score_type: "ScoreType | None" = None,
    ):
        """Initialize collision response.

        Args:
            remove: Remove the entity after collision
            damage: Damage Mario
            power_up_type: Specific power-up identifier (e.g., "mushroom")
            bounce_velocity: Upward velocity to apply to Mario (e.g., for stomping)
            spawn_entity: Entity to spawn after collision (e.g., Koopa shell)
            score_type: Optional score classification for combo tracking
        """
        self.remove = remove
        self.damage = damage
        self.power_up_type = power_up_type
        self.bounce_velocity = bounce_velocity
        self.spawn_entity = spawn_entity
        self.score_type = score_type


class Entity(ABC, Drawable):
    """Base class for all game entities."""

    z_index: int = 10

    def __init__(self, world_x: float, world_y: float, screen: int = 0):
        """Initialize entity.

        Args:
            world_x: X position in world pixels
            world_y: Y position in screen-relative pixels (0-224, from bottom)
            screen: Which vertical screen the entity is on
        """
        self.state = EntityState(x=world_x, y=world_y, screen=screen)
        self._pipeline: Optional[EntityPipeline] = None

    @abstractmethod
    def update(self, dt: float, level: Level) -> bool:
        """Update entity state.

        Args:
            dt: Delta time in seconds
            level: Level for collision detection

        Returns:
            True if entity should remain active, False to remove
        """

    @abstractmethod
    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the entity.

        Args:
            surface: Surface to draw on
            camera: Camera for coordinate transformation
        """

    def get_collision_bounds(self) -> Rect:
        """Get collision rectangle for this entity.

        Returns:
            Pygame Rect representing collision bounds
        """
        return Rect(
            int(self.state.x),
            int(self.state.y),
            int(self.state.width),
            int(self.state.height),
        )

    def on_collide_mario(self, mario: "Mario") -> Optional[CollisionResponse]:
        """Handle collision with Mario.

        Args:
            mario_state: Mario's current state

        Returns:
            CollisionResponse describing what should happen, or None for no response
        """
        return None

    @property
    def is_stompable(self) -> bool:
        """Check if this entity can be stomped by Mario.

        Returns:
            True if entity can be stomped, False otherwise
        """
        return False

    @property
    def can_damage_entities(self) -> bool:
        """Whether this entity inflicts damage on other entities when colliding."""
        return False

    @property
    def can_be_damaged_by_entities(self) -> bool:
        """Whether this entity can be damaged by other entities."""
        return False

    @property
    def blocks_entities(self) -> bool:
        """Whether this entity blocks other entities when colliding."""
        return False

    @property
    def awards_shell_combo(self) -> bool:
        """Whether defeating this entity with a shell advances the combo."""
        return False

    def on_collide_entity(self, source: "Entity") -> bool:
        """Handle collision with another entity.

        Args:
            source: The entity that initiated the collision.

        Returns:
            True if this entity should be removed after the collision, False otherwise.
        """
        return False

    def is_off_screen(self, mario_screen: int, camera_x: float) -> bool:
        """Check if entity is off screen and should be removed.

        Only removes entities that are behind or below the viewport.
        Entities ahead of the viewport are kept active.

        Args:
            mario_screen: Mario's current screen
            camera_x: Camera X position

        Returns:
            True if entity should be culled
        """
        entity_right = self.state.x + self.state.width
        screen_left = camera_x

        MARGIN = TILE_SIZE * 2
        BELOW_SCREEN_THRESHOLD = -100

        if entity_right < screen_left - MARGIN:
            return True

        if self.state.y < BELOW_SCREEN_THRESHOLD:
            return True

        return False

    def configure_size(self, width: float, height: float) -> None:
        """Helper to configure the entity's collision dimensions."""
        self.state.width = width
        self.state.height = height

    def build_pipeline(self) -> Optional[EntityPipeline]:
        """Create the entity physics pipeline (override in subclasses)."""
        return None

    def set_pipeline(self) -> None:
        """Build and cache the entity pipeline."""
        self._pipeline = self.build_pipeline()

    def process_pipeline(self, dt: float, level: "Level") -> None:
        """Execute the entity pipeline if one is configured."""
        if self._pipeline is None:
            return

        context = EntityPhysicsContext(
            entity=self,
            state=self.state,
            level=level,
            dt=dt,
        )
        self._pipeline.process(context)
