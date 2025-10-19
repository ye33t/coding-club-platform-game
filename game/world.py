"""World physics and game logic."""

from typing import Iterator, Optional, cast

from .camera import Camera
from .constants import TILE_SIZE
from .effects import EffectManager
from .entities import EntityFactory, EntityManager
from .gameplay import (
    HUD_COIN_DIGITS,
    HUD_COIN_INCREMENT,
    HUD_COIN_SCORE_VALUE,
    HUD_DEFAULT_TIMER_START,
    HUD_SCORE_DIGITS,
    HUD_TIMER_DIGITS,
    HUD_TIMER_FRAMES_PER_DECREMENT,
)
from .hud import HudDimensions, HudState
from .levels import loader
from .mario import Mario
from .physics import PhysicsContext, PhysicsPipeline
from .physics.events import PhysicsEvent
from .props import FlagpoleProp, PropManager
from .rendering.base import Drawable


class World:
    """Manages game physics and collision logic."""

    def __init__(self) -> None:
        """Initialize the world."""
        # Load the default level
        self.level = loader.load("game/assets/levels/world_1_1.yaml")
        self.camera = Camera()
        self.physics = PhysicsPipeline()
        self.effects = EffectManager()
        self.entities = EntityManager()
        self.entity_factory = EntityFactory()
        self.props = PropManager()
        self.props.register("flagpole", FlagpoleProp())
        self.animation_tick = 0

        # Create Mario at the level's spawn point
        self.mario = Mario(
            self.level.spawn_x,
            self.level.spawn_y,
            self.level.spawn_screen,
        )

        hud_dimensions = HudDimensions(
            score_digits=HUD_SCORE_DIGITS,
            coin_digits=HUD_COIN_DIGITS,
            timer_digits=HUD_TIMER_DIGITS,
        )
        self.hud = HudState(hud_dimensions)
        self._configure_hud_for_level(preserve_progress=False)

        self.props.spawn_all(self)

    def reset(self) -> None:
        """Reset the world to the level's spawn configuration."""
        # Reset Mario to the spawn point defined by the level
        self.mario.reset(
            x=self.level.spawn_x,
            y=self.level.spawn_y,
            screen=self.level.spawn_screen,
        )

        # Reset terrain and transient systems to their initial state
        self.level.reset_terrain()
        self.effects.clear()
        self.entities.clear()
        self.props.reset(self)

        # Reset all spawn triggers back to their pending state
        self.level.spawn_manager.reset_all_triggers()

        # Reset camera position and ratchet
        self.camera.x = 0
        self.camera.max_x = 0
        self.animation_tick = 0
        self._configure_hud_for_level(preserve_progress=False)

    def update(self, keys, dt: float) -> Optional[PhysicsEvent]:
        """Process Mario's intent and update his state.

        Returns:
            Physics event if one was raised (e.g., death, warp), None otherwise
        """
        self.mario.update_intent(keys)
        self.hud.tick_timer()

        self.entities.update(dt, self.level, self.mario.screen, self.camera.x)

        context = PhysicsContext(
            dt=dt,
            mario=self.mario,
            camera=self.camera,
            level=self.level,
            entities=self.entities.items,
            props=self.props,
        )

        processed_context = self.physics.process(context)

        triggered_event: Optional[PhysicsEvent] = None
        for event in processed_context.events:
            if event.dispatch(self, processed_context):
                triggered_event = cast(PhysicsEvent, event)
                break

        if triggered_event is not None:
            self.animation_tick += 1
            return triggered_event

        self.props.update(self, dt)
        self.effects.update(dt)

        self.camera.update(self.mario.x, self.level.width_pixels)

        self._check_spawn_triggers()

        self.animation_tick += 1

        return None

    @property
    def drawables(self) -> Iterator[Drawable]:
        """Iterate over drawable objects with z-index for rendering."""

        def _iter() -> Iterator[Drawable]:
            yield self.mario
            yield from self.effects._effects
            yield from self.entities._entities

        return _iter()

    def _check_spawn_triggers(self) -> None:
        """Check and activate spawn triggers based on camera position."""
        # Get triggered spawn triggers
        triggered = self.level.spawn_manager.check_triggers(self.camera.x)

        # Spawn entities for each triggered trigger
        for trigger in triggered:
            for entity_spec in trigger.entities:
                # Spawn each entity at all its locations
                for tile_x, tile_y, screen in entity_spec.locations:
                    world_x = tile_x * TILE_SIZE
                    world_y = tile_y * TILE_SIZE

                    entity = self.entity_factory.create(
                        entity_spec.entity_type,
                        world_x,
                        world_y,
                        screen,
                        entity_spec.params,
                    )
                    if entity:
                        self.entities.spawn(entity)

    def _configure_hud_for_level(self, preserve_progress: bool) -> None:
        """Apply level-specific HUD configuration."""
        timer_start = (
            self.level.timer_start_value
            if self.level.timer_start_value is not None
            else HUD_DEFAULT_TIMER_START
        )
        frames_per_decrement = (
            self.level.timer_frames_per_decrement
            if self.level.timer_frames_per_decrement is not None
            else HUD_TIMER_FRAMES_PER_DECREMENT
        )
        display_label = self.level.display_label()
        self.hud.configure_for_level(
            display_label=display_label,
            timer_start=timer_start,
            frames_per_decrement=frames_per_decrement,
            preserve_progress=preserve_progress,
        )

    def award_score(self, amount: int) -> None:
        """Increment the global score."""
        self.hud.add_score(amount)

    def collect_coin(self, amount: Optional[int] = None) -> None:
        """Increment coin counter and associated score bonus."""
        coins_to_add = amount if amount is not None else HUD_COIN_INCREMENT
        if coins_to_add <= 0:
            return
        self.hud.add_coins(coins_to_add)
        self.hud.add_score(HUD_COIN_SCORE_VALUE * coins_to_add)
