"""Base classes for game entities (enemies and collectibles)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from pygame import Rect, Surface

from ..camera import Camera
from ..constants import TILE_SIZE

if TYPE_CHECKING:
    from ..level import Level
    from ..mario import MarioState


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
    direction: int = 1
    on_ground: bool = False


class CollisionResponse:
    """Response to collision with Mario."""

    def __init__(
        self,
        remove: bool = False,
        damage: bool = False,
        power_up_type: Optional[str] = None,
        bounce_velocity: Optional[float] = None,
    ):
        """Initialize collision response.

        Args:
            remove: Remove the entity after collision
            damage: Damage Mario
            power_up_type: Specific power-up identifier (e.g., "mushroom")
            bounce_velocity: Upward velocity to apply to Mario (e.g., for stomping)
        """
        self.remove = remove
        self.damage = damage
        self.power_up_type = power_up_type
        self.bounce_velocity = bounce_velocity


class Entity(ABC):
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

    def on_collide_mario(self, mario_state: MarioState) -> Optional[CollisionResponse]:
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
