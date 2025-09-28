"""World physics and game logic."""

from .camera import Camera
from .collision_shapes import TileCollision
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

        # Height-based collision detection for slopes and regular tiles
        # Mario is 2 tiles wide, 2 tiles tall
        mario_width = 2 * TILE_SIZE
        mario_height = 2 * TILE_SIZE

        # Check ceiling collision (when moving upward)
        if new_state.vy > 0:
            # Check for ceiling collision at Mario's NEW head position
            # Allow 2 pixels of penetration for better game feel
            head_y = new_state.y + mario_height - 2

            # Sample points across Mario's width for ceiling
            ceiling_sample_points = [
                new_state.x + 1,  # Slightly inset to avoid edge issues
                new_state.x + mario_width / 2,
                new_state.x + mario_width - 2,
            ]

            for sample_x in ceiling_sample_points:
                tile_x = int(sample_x // TILE_SIZE)
                tile_y = int(head_y // TILE_SIZE)

                tile_type = self.level.get_tile(tile_x, tile_y)
                if tile_type != 0 and self.level.is_solid(tile_type):
                    # Mario's head penetrated into a solid tile
                    # Push him back down but allow slight penetration for better feel
                    new_state.y = (tile_y * TILE_SIZE) - mario_height + 2
                    new_state.vy = 0  # Stop upward movement
                    break

        # Check ground collision by sampling multiple points along Mario's width
        highest_ground = -1.0  # Start with invalid value
        found_ground = False

        # Sample at left edge, center, and right edge
        sample_points = [
            new_state.x,
            new_state.x + mario_width / 2,
            new_state.x + mario_width - 1,
        ]

        for sample_x in sample_points:
            # Get tile coordinates
            tile_x = int(sample_x // TILE_SIZE)

            # Check tiles from 2 below to 1 above Mario's position
            # This ensures we catch slopes that extend into adjacent tiles
            base_tile_y = int(new_state.y // TILE_SIZE)

            for check_y in range(base_tile_y - 2, base_tile_y + 2):
                if check_y < 0 or check_y >= self.level.height_tiles:
                    continue

                tile_type = self.level.get_tile(tile_x, check_y)
                if tile_type != 0:
                    # Calculate position within tile
                    x_offset = sample_x - (tile_x * TILE_SIZE)

                    # Get ground height at this position
                    ground_height = TileCollision.get_ground_height(tile_type, x_offset)
                    if ground_height is not None:
                        # Convert to world coordinates
                        world_ground_y = check_y * TILE_SIZE + ground_height

                        # Check if Mario is within collision range of this ground
                        # Allow a small margin for floating point precision
                        if (
                            abs(new_state.y - world_ground_y) <= 2.0
                            or new_state.y < world_ground_y
                        ):
                            if new_state.y <= world_ground_y + 1:
                                found_ground = True
                                if (
                                    highest_ground < 0
                                    or world_ground_y > highest_ground
                                ):
                                    highest_ground = world_ground_y

        # Apply ground collision
        if found_ground and new_state.vy <= 0:
            new_state.y = highest_ground
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
