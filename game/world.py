"""World physics and game logic."""

from typing import Iterator, Optional, cast

from .camera import Camera
from .constants import SUB_TILE_SIZE, TILE_SIZE
from .effects import EffectManager, SpriteEffect
from .entities import EntityFactory, EntityManager
from .levels import loader
from .mario import Mario
from .physics import PhysicsContext, PhysicsPipeline
from .physics.events import PhysicsEvent
from .rendering.base import Drawable
from .terrain.flagpole import FlagpoleBehavior


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

        self._flagpole_flag: SpriteEffect | None = None

        # Create Mario at the level's spawn point
        self.mario = Mario(
            self.level.spawn_x,
            self.level.spawn_y,
            self.level.spawn_screen,
        )

        self._spawn_flagpole_flag()

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

        self._flagpole_flag = None
        self._spawn_flagpole_flag()

        # Reset all spawn triggers back to their pending state
        self.level.spawn_manager.reset_all_triggers()

        # Reset camera position and ratchet
        self.camera.x = 0
        self.camera.max_x = 0

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
        )

        processed_context = self.physics.process(context)

        for event in processed_context.events:
            if event.dispatch(self, processed_context):
                return cast(PhysicsEvent, event)

        self.effects.update(dt)

        self.camera.update(self.mario.x, self.level.width_pixels)

        self._check_spawn_triggers()

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

    def _spawn_flagpole_flag(self) -> None:
        """Spawn the decorative flag sprite at the top of the flagpole."""
        flagpole_tiles = [
            instance
            for instance in self.level.terrain_manager.instances.values()
            if isinstance(instance.behavior, FlagpoleBehavior)
        ]

        if not flagpole_tiles:
            return

        top_tile = max(flagpole_tiles, key=lambda tile: tile.y)
        pole_x = top_tile.x * TILE_SIZE + SUB_TILE_SIZE - 1
        pole_top_y = (top_tile.y - 1) * TILE_SIZE

        flag_x = pole_x - TILE_SIZE
        flag_bottom_y = pole_top_y

        flag_effect = SpriteEffect(
            sprite_sheet="other",
            sprite_name="flag",
            world_x=flag_x,
            world_y=flag_bottom_y,
            z_index=5,
        )

        self.effects.spawn(flag_effect)
        self._flagpole_flag = flag_effect
