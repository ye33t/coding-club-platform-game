"""Reusable mixins that compose entity behaviors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Sequence

from .physics import (
    EntityPipeline,
    GravityProcessor,
    GroundSnapProcessor,
    HorizontalVelocityProcessor,
    VelocityIntegrator,
    WallBounceProcessor,
)

if TYPE_CHECKING:
    from .base import Entity, EntityState
    from .physics.base import EntityProcessor


@dataclass(slots=True)
class HorizontalMovementConfig:
    """Configuration for horizontal walker style entities."""

    gravity: float
    speed: float
    ground_snap_tolerance: float


class HorizontalMovementMixin:
    """Provide standard horizontal movement pipeline and helpers."""

    state: "EntityState"
    _horizontal_movement_config: HorizontalMovementConfig
    _horizontal_processor: HorizontalVelocityProcessor
    _wall_bounce_processor: WallBounceProcessor

    def init_horizontal_movement(self, config: HorizontalMovementConfig) -> None:
        """Initialize reusable processors based on the supplied config."""
        self._horizontal_movement_config = config
        self._horizontal_processor = HorizontalVelocityProcessor(speed=config.speed)
        self._wall_bounce_processor = WallBounceProcessor(speed=config.speed)

    def build_pipeline(self) -> Optional[EntityPipeline]:
        """Build the standard gravity → walk → integrate → bounce → snap pipeline."""
        config = self._horizontal_movement_config
        processors: List["EntityProcessor"] = [
            GravityProcessor(gravity=config.gravity),
            self._horizontal_processor,
            VelocityIntegrator(),
            self._wall_bounce_processor,
            GroundSnapProcessor(tolerance=config.ground_snap_tolerance),
        ]
        processors.extend(self.additional_movement_processors())
        return EntityPipeline(processors)

    def additional_movement_processors(self) -> Sequence["EntityProcessor"]:
        """Hook for subclasses to append extra processors."""
        return ()

    def handle_blocking_entity(self, source: "Entity") -> None:
        """Flip facing direction and snap next to a blocking entity."""
        state = self.state
        if state.facing_right:
            state.facing_right = False
            state.x = source.state.x - state.width
        else:
            state.facing_right = True
            state.x = source.state.x + source.state.width

        speed = self._horizontal_processor.speed
        state.vx = speed if state.facing_right else -speed


@dataclass(slots=True)
class KnockoutSettings:
    """Configuration for entity knockout behavior."""

    vertical_velocity: float
    horizontal_velocity: float
    gravity: float
    removal_floor: float = -100.0


class KnockoutMixin:
    """Handle shared 'knocked out' physics and responses."""

    state: "EntityState"
    knocked_out: bool
    _knockout_settings: KnockoutSettings

    def init_knockout(self, settings: KnockoutSettings) -> None:
        """Configure knockout physics parameters."""
        self.knocked_out = False
        self._knockout_settings = settings

    def update_knockout(self, dt: float) -> Optional[bool]:
        """Advance knockout physics if active, returning keep-alive status."""
        if not self.knocked_out:
            return None

        state = self.state
        settings = self._knockout_settings

        state.vy -= settings.gravity * dt
        state.x += state.vx * dt
        state.y += state.vy * dt

        return state.y >= settings.removal_floor

    def trigger_knockout(self, source: "Entity") -> None:
        """Activate knockout state and configure launch velocities."""
        if self.knocked_out:
            return

        self.knocked_out = True
        settings = self._knockout_settings
        state = self.state

        state.vy = settings.vertical_velocity

        if source.state.vx > 0:
            direction = 1
        elif source.state.vx < 0:
            direction = -1
        else:
            direction = -1 if source.state.x < state.x else 1

        state.vx = settings.horizontal_velocity * direction
        self.on_knockout(source)

    def on_knockout(self, source: "Entity") -> None:
        """Hook for subclasses to adjust additional state on knockout."""
        return
