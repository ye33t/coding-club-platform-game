"""World physics and game logic."""

from .camera import Camera
from .levels import loader
from .mario import Mario
from .physics import PhysicsContext, PhysicsPipeline


class World:
    """Manages game physics and collision logic."""

    def __init__(self):
        """Initialize the world."""
        # Load the default level
        self.level = loader.load("game/assets/levels/world_1_1.yaml")
        self.camera = Camera()
        self.physics_pipeline = PhysicsPipeline()

        # Create Mario at the level's spawn point
        self.mario = Mario(
            self.level.spawn_x,
            self.level.spawn_y,
            self.level.spawn_screen,
        )

    def update(self, keys, dt: float):
        """Process Mario's intent and update his state."""
        # Step 1: Get Mario's intent from input
        mario_intent = self.mario.get_intent(keys)

        # Step 2: Create physics context with cloned states
        context = PhysicsContext(
            mario_state=self.mario.state.clone(),  # Work with a copy
            mario_intent=mario_intent,
            level=self.level,
            camera_state=self.camera.state.clone(),  # Work with a copy
            dt=dt,
        )

        # Step 3: Process through physics pipeline
        processed_context = self.physics_pipeline.process(context)

        # Step 4: Push state back to Mario
        self.mario.apply_state(processed_context.mario_state)

        # Step 5: Apply camera state changes
        self.camera.apply_state(processed_context.camera_state)

        # Step 6: Update Mario's animation
        self.mario.update_animation()

        # Step 7: Update terrain behaviors
        self.level.terrain_manager.update(dt)

        # Step 8: Update camera based on Mario's new position
        self.camera.update(self.mario.state.x, self.level.width_pixels)
