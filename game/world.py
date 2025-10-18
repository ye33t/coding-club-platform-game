"""World physics and game logic."""

from typing import Iterator, Optional, cast

from .camera import Camera
from .constants import TILE_SIZE
from .effects import EffectManager
from .entities import EntityFactory, EntityManager
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

    def update(self, keys, dt: float) -> Optional[PhysicsEvent]:
        """Process Mario's intent and update his state.

        Returns:
            Physics event if one was raised (e.g., death, warp), None otherwise
        """
        self.mario.update_intent(keys)

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
