"""Central physics constants for the game.

All physics-related constants should be defined here to ensure consistency
and make tuning easier.
"""

# Movement speeds (pixels per second)
WALK_SPEED = 85.0
RUN_SPEED = 140.0

# Jump velocities (pixels per second)
WALK_JUMP_VELOCITY = 226.0  # ~4 blocks high
RUN_JUMP_VELOCITY = 277.0  # ~6 blocks high

# Gravity (pixels per second squared)
GRAVITY = 400.0
JUMP_CUT_MULTIPLIER = 3.0  # Multiply gravity when jump button released early

# Acceleration constants (pixels per second²)
GROUND_ACCELERATION = 180.0  # Normal ground acceleration
SKID_DECELERATION = 600.0  # Deceleration when skidding
AIR_ACCELERATION = 120.0  # Air control

# Friction constants
MIN_FRICTION = 0.88  # At high speeds (more sliding)
MAX_FRICTION = 0.60  # At low speeds (quick stops)
FRICTION_SPEED_RANGE = 30.0  # Speed range over which friction varies (fixed from 80)

# Action thresholds
RUN_SPEED_THRESHOLD = 100.0  # Speed to determine run action/jump (between walk=85 and run=140)
SKID_THRESHOLD = 100.0  # Speed difference that triggers skidding (fixed from 80)

# Terrain-specific physics
BOUNCE_VELOCITY = 60.0  # Initial upward velocity for bounce blocks
BOUNCE_GRAVITY = 400.0  # Gravity for bounce blocks

# Death animation
DEATH_LEAP_VELOCITY = 200.0  # Initial upward velocity for death leap