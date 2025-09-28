"""World physics and game logic."""

from .camera import Camera
from .level import Level
from .mario import Mario
from .physics import PhysicsContext, PhysicsPipeline


class World:
    """Manages game physics and collision logic."""

    def __init__(self):
        """Initialize the world."""
        # Create level and camera
        self.level = Level(width_in_screens=3)  # 3 screens wide for testing
        self.camera = Camera()

        # Create physics pipeline
        self.physics_pipeline = PhysicsPipeline()

    def process_mario(self, mario: Mario, keys, dt: float):
        """Process Mario's intent and update his state."""
        # Step 1: Get Mario's intent from input
        intent = mario.read_input(keys)

        # Step 2: Create physics context
        context = PhysicsContext(
            state=mario.state.clone(),  # Work with a copy
            intent=intent,
            dt=dt,
            level=self.level,
            camera=self.camera,
        )

        # Step 3: Process through physics pipeline
        processed_context = self.physics_pipeline.process(context)

        # Step 4: Check if reset is needed
        if processed_context.state.should_reset:
            # Reset Mario to starting position
            from .mario import MarioState
            mario.state = MarioState(x=50.0, y=16.0)
            # Reset camera to beginning (both position and ratchet)
            self.camera.x = 0
            self.camera.max_x = 0
            return  # Skip the rest of the update

        # Step 5: Push state back to Mario
        mario.apply_state(processed_context.state)

        # Step 6: Update Mario's animation
        mario.update_animation()

        # Step 7: Update camera based on Mario's new position
        self.camera.update(mario.state.x, self.level.width_pixels)
