"""World physics and game logic."""

from typing import Any, List, Optional

from .camera import Camera
from .effects import EffectManager
from .entities import EntityManager
from .levels import loader
from .mario import Mario
from .physics import PhysicsContext, PhysicsPipeline
from .physics.events import PhysicsEvent


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

        # Step 3: Create physics context with cloned states
        context = PhysicsContext(
            mario_state=self.mario.state.clone(),  # Work with a copy
            mario_intent=mario_intent,
            level=self.level,
            camera_state=self.camera.state.clone(),  # Work with a copy
            dt=dt,
            entities=self.entities.get_entities(),
        )

        # Step 4: Process through physics pipeline
        processed_context = self.physics_pipeline.process(context)

        # Apply any tile or effect commands queued during behavior processing.
        self.level.terrain_manager.apply_pending_commands(
            self.level, self.effects, self.entities
        )

        # Step 5: Check if an event was raised (short-circuits normal processing)
        event: Optional[PhysicsEvent] = processed_context.event
        if event is not None:
            return event

        # Step 6: Push state back to Mario
        self.mario.apply_state(processed_context.mario_state)

        # Step 7: Apply camera state changes
        self.camera.apply_state(processed_context.camera_state)

        # Step 8: Update Mario's animation
        self.mario.update_animation()

        # Step 9: Update terrain behaviors
        self.level.terrain_manager.update(dt)

        # Step 10: Update transient effects
        self.effects.update(dt)

        # Step 11: Update camera based on Mario's new position
        self.camera.update(self.mario.state.x, self.level.width_pixels)

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
