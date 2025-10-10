"""Load physics configuration from TOML file."""

import tomllib
from pathlib import Path

# Load config file - fail fast if missing or invalid
CONFIG_PATH = Path(__file__).parent.parent / "assets" / "config" / "physics.toml"

try:
    with open(CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)
except FileNotFoundError:
    raise FileNotFoundError(
        f"Physics config file not found: {CONFIG_PATH}\n"
        "The game requires physics.toml to run."
    )
except tomllib.TOMLDecodeError as e:
    raise ValueError(f"Invalid TOML in physics config: {CONFIG_PATH}\n" f"Error: {e}")

# Movement
WALK_SPEED = config["movement"]["walk_speed"]
RUN_SPEED = config["movement"]["run_speed"]
STOP_THRESHOLD = config["movement"]["stop_threshold"]

# Jumping
WALK_JUMP_VELOCITY = config["jumping"]["walk_jump_velocity"]
RUN_JUMP_VELOCITY = config["jumping"]["run_jump_velocity"]
RUN_SPEED_THRESHOLD = config["jumping"]["run_speed_threshold"]

# Gravity
GRAVITY = config["gravity"]["gravity"]
JUMP_CUT_MULTIPLIER = config["gravity"]["jump_cut_multiplier"]

# Acceleration
GROUND_ACCELERATION = config["acceleration"]["ground_acceleration"]
SKID_DECELERATION = config["acceleration"]["skid_deceleration"]
AIR_ACCELERATION = config["acceleration"]["air_acceleration"]

# Friction
MIN_FRICTION = config["friction"]["min_friction"]
MAX_FRICTION = config["friction"]["max_friction"]
FRICTION_SPEED_RANGE = config["friction"]["friction_speed_range"]

# Action
SKID_THRESHOLD = config["action"]["skid_threshold"]
SKID_CLEAR_VELOCITY = config["action"]["skid_clear_velocity"]
STOP_VELOCITY = config["action"]["stop_velocity"]
WALK_THRESHOLD = config["action"]["walk_threshold"]
ANIMATION_SPEED_SCALE = config["action"]["animation_speed_scale"]

# Collision
WALL_DEAD_ZONE = config["collision"]["wall_dead_zone"]
CEILING_DEAD_ZONE = config["collision"]["ceiling_dead_zone"]
CEILING_SAMPLE_EDGE_OFFSET = config["collision"]["ceiling_sample_edge_offset"]
WALL_SAMPLE_TOP_OFFSET = config["collision"]["wall_sample_top_offset"]
CEILING_BOUNCE_VELOCITY = config["collision"]["ceiling_bounce_velocity"]

# Terrain
BOUNCE_VELOCITY = config["terrain"]["bounce_velocity"]
BOUNCE_GRAVITY = config["terrain"]["bounce_gravity"]
BOUNCE_DURATION = config["terrain"]["bounce_duration"]

# Death
DEATH_LEAP_VELOCITY = config["death"]["death_leap_velocity"]
RESET_THRESHOLD_Y = config["death"]["reset_threshold_y"]

# Flagpole
FLAGPOLE_TRIGGER_DISTANCE = config["flagpole"]["trigger_distance"]
FLAGPOLE_DESCENT_SPEED = config["flagpole"]["descent_speed"]

# Coin
COIN_JUMP_VELOCITY = config["coin"]["jump_velocity"]
COIN_GRAVITY = config["coin"]["gravity"]
COIN_OFFSET = config["coin"]["offset"]

# Power-ups
MARIO_TRANSITION_MS = config["powerups"]["mario_transition_ms"]
MARIO_TRANSITION_DURATION = MARIO_TRANSITION_MS / 1000.0

# Warp (hardcoded - not user-tunable)
WARP_SPEED = 16.0  # pixels/second (1 tile per second)
