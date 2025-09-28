"""World physics and game logic."""

from .camera import Camera
from .constants import TILE_SIZE
from .level import Level
from .mario import Mario, MarioIntent, MarioState

# Physics constants
GRAVITY = 400.0  # pixels per second squared
WALK_SPEED = 64.0  # pixels per second
RUN_SPEED = 128.0  # pixels per second
JUMP_VELOCITY = 200.0  # pixels per second
FRICTION = 0.85  # speed multiplier when decelerating
SKID_THRESHOLD = 80.0  # speed difference that triggers skidding


class World:
    """Manages game physics and collision logic."""

    def __init__(self):
        """Initialize the world."""
        # Create level and camera
        self.level = Level(width_in_screens=3)  # 3 screens wide for testing
        self.camera = Camera()

    def process_mario(self, mario: Mario, keys, dt: float):
        """Process Mario's intent and update his state."""
        # Step 1: Get Mario's intent from input
        intent = mario.read_input(keys)

        # Step 2: Get current state
        current_state = mario.state

        # Step 3: Calculate new state based on intent + physics
        new_state = self.resolve_intent(current_state, intent, dt)

        # Step 4: Push state back to Mario
        mario.apply_state(new_state)

        # Step 5: Update Mario's animation
        mario.update_animation()

        # Step 6: Update camera based on Mario's new position
        self.camera.update(mario.state.x, self.level.width_pixels)

    def resolve_intent(
        self, state: MarioState, intent: MarioIntent, dt: float
    ) -> MarioState:
        """Turn intent into reality with physics and game rules."""
        # Clone the state to work with
        new_state: MarioState = state.clone()

        # Handle horizontal movement intent
        target_vx = 0.0

        if intent.move_right:
            target_vx = RUN_SPEED if intent.run else WALK_SPEED
            # Check for skidding (trying to reverse direction quickly)
            if new_state.vx < -SKID_THRESHOLD and new_state.on_ground:
                new_state.action = "skidding"
            else:
                new_state.facing_right = True

        elif intent.move_left:
            target_vx = -(RUN_SPEED if intent.run else WALK_SPEED)
            # Check for skidding
            if new_state.vx > SKID_THRESHOLD and new_state.on_ground:
                new_state.action = "skidding"
            else:
                new_state.facing_right = False

        # Apply acceleration/deceleration
        if target_vx != 0:
            # Accelerate toward target velocity
            new_state.vx = target_vx
        else:
            # Decelerate with friction
            new_state.vx *= FRICTION
            if abs(new_state.vx) < 1.0:
                new_state.vx = 0.0

        # Handle jump intent
        if intent.jump and state.on_ground:
            new_state.vy = JUMP_VELOCITY
            new_state.on_ground = False

        # Apply gravity
        if not new_state.on_ground:
            new_state.vy -= GRAVITY * dt

        # Calculate new position
        new_state.x += new_state.vx * dt
        new_state.y += new_state.vy * dt

        # Check world boundaries
        # Mario can't go left of the camera position (ratcheting)
        if new_state.x < self.camera.x:
            new_state.x = self.camera.x
            new_state.vx = 0
        elif new_state.x > self.level.width_pixels - 16:  # Mario is 2 tiles wide
            new_state.x = self.level.width_pixels - 16
            new_state.vx = 0

        # Tile-based collision detection
        # Mario is 2 tiles wide, 2 tiles tall
        mario_width = 2 * TILE_SIZE

        # Check for ground collision
        # Check one pixel below Mario's feet
        ground_check_y = new_state.y - 1
        if (
            self.level.get_tile_at_position(new_state.x, ground_check_y) != 0
            or self.level.get_tile_at_position(
                new_state.x + mario_width - 1, ground_check_y
            )
            != 0
        ):
            # Snap to top of tile
            tile_y = int(ground_check_y // TILE_SIZE)
            new_state.y = (tile_y + 1) * TILE_SIZE
            new_state.vy = 0
            new_state.on_ground = True
        else:
            new_state.on_ground = False

        # Determine action based on final physics state
        if new_state.action != "skidding" or abs(new_state.vx) < 10:
            # Not skidding or stopped skidding
            new_state.action = self.determine_action(new_state)

        return new_state

    def determine_action(self, state: MarioState) -> str:
        """Determine Mario's action based on his physics state."""
        if not state.on_ground:
            return "jumping"
        elif abs(state.vx) > RUN_SPEED * 0.8:
            return "running"
        elif abs(state.vx) > 1.0:
            return "walking"
        else:
            return "idle"
