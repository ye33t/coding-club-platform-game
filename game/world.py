"""World physics and game logic."""

from copy import deepcopy
from typing import TYPE_CHECKING, Any, List, Optional

from .camera import Camera
from .effects import EffectManager
from .entities import EntityFactory, EntityManager
from .levels import loader
from .mario import Mario
from .physics import PhysicsContext, PhysicsPipeline
from .physics.events import PhysicsEvent

if TYPE_CHECKING:
    from .mario import MarioState


class World:
    """Manages game physics and collision logic."""

    def __init__(self):
        """Initialize the world."""
        # Load the default level
        self.level = loader.load("game/assets/levels/world_1_1.yaml")
        self.camera = Camera()
        self.physics_pipeline = PhysicsPipeline()
        self.effects = EffectManager()
        self.entities = EntityManager()
        self.entity_factory = EntityFactory()

        # Create Mario at the level's spawn point
        self.mario = Mario(
            self.level.spawn_x,
            self.level.spawn_y,
            self.level.spawn_screen,
        )

    def update(self, keys, dt: float) -> Optional[PhysicsEvent]:
        """Process Mario's intent and update his state.

        Returns:
            Physics event if one was raised (e.g., death, warp), None otherwise
        """
        # Step 1: Get Mario's intent from input
        mario_intent = self.mario.get_intent(keys)

        # Step 2: Update entities physics (before Mario physics)
        self.entities.update(dt, self.level, self.mario.state.screen, self.camera.x)

        # Capture pre-physics state for animation updates and event rollbacks
        pre_mario_state = deepcopy(self.mario.state)
        pre_camera_values = (self.camera.x, self.camera.max_x)

        # Step 3: Create physics context that operates on live objects
        context = PhysicsContext(
            mario=self.mario,
            camera=self.camera,
            mario_intent=mario_intent,
            level=self.level,
            dt=dt,
            entities=self.entities.get_entities(),
        )

        # Step 4: Process through physics pipeline
        processed_context = self.physics_pipeline.process(context)

        # Apply any tile or effect commands queued during behavior processing.
        self.level.terrain_manager.apply_pending_commands(
            self.level, self.effects, self.entities
        )

        # Remove any entities flagged during physics processing
        self.entities.remove_entities(processed_context.entities_to_remove)

        # Step 5: Check if an event was raised (short-circuits normal processing)
        event: Optional[PhysicsEvent] = processed_context.event
        if event is not None:
            self._restore_pre_physics_state(pre_mario_state, pre_camera_values)
            return event

        # Step 6: Update Mario's animation state with the pre-physics snapshot
        self.mario.post_physics_update(pre_mario_state)

        # Step 7: Update Mario's animation
        self.mario.update_animation()

        # Step 8: Update terrain behaviors
        self.level.terrain_manager.update(dt)

        # Step 9: Update transient effects
        self.effects.update(dt)

        # Step 10: Update camera based on Mario's new position
        self.camera.update(self.mario.state.x, self.level.width_pixels)

        # Step 11: Check spawn triggers based on camera position
        self._check_spawn_triggers()

        return None

    def get_drawables(self) -> List[Any]:
        """Get all drawable objects with z-index for rendering.

        Returns:
            List of all drawable objects (Mario, effects, entities)
        """
        drawables: List[Any] = [self.mario]
        drawables.extend(self.effects._effects)
        drawables.extend(self.entities._entities)
        return drawables

    def _check_spawn_triggers(self) -> None:
        """Check and activate spawn triggers based on camera position."""
        from .constants import TILE_SIZE

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

    def reset_spawn_triggers(self) -> None:
        """Reset all spawn triggers and clear enemy entities.

        Called when restarting after death, warp, or level reset.
        """
        # Reset all triggers to pending state
        self.level.spawn_manager.reset_all_triggers()

        # Clear all entities (enemies and collectibles)
        self.entities.clear()

    def _restore_pre_physics_state(
        self, mario_state: "MarioState", camera_values: tuple[float, float]
    ) -> None:
        """Restore Mario and camera state when physics short-circuits.

        Args:
            mario_state: Snapshot of Mario's state captured pre-physics
            camera_values: Snapshot of the camera's state captured pre-physics
        """
        self.mario.state = mario_state
        self.camera.x, self.camera.max_x = camera_values
