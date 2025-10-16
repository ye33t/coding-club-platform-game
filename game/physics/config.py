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

# transitions
MARIO_TRANSITION_DURATION = config["transitions"]["duration"]
MARIO_TRANSITION_INTERVAL = config["transitions"]["interval"]

# Stomp
STOMP_VELOCITY_Y_SCALE = config["stomp"]["velocity_y_scale"]

# Warp (hardcoded - not user-tunable)
WARP_SPEED = 16.0  # pixels/second (1 tile per second)

# Goomba enemy
GOOMBA_SPEED = config["goomba"]["speed"]
GOOMBA_GRAVITY = config["goomba"]["gravity"]
GOOMBA_GROUND_TOLERANCE = config["goomba"]["ground_tolerance"]
GOOMBA_ANIMATION_FPS = config["goomba"]["animation_fps"]
GOOMBA_STOMP_BOUNCE_VELOCITY = config["goomba"]["stomp_bounce_velocity"]
GOOMBA_DEATH_DURATION = config["goomba"]["death_duration"]

# Mushroom collectible
MUSHROOM_SPEED = config["mushroom"]["speed"]
MUSHROOM_GRAVITY = config["mushroom"]["gravity"]
MUSHROOM_EMERGE_SPEED = config["mushroom"]["emerge_speed"]
MUSHROOM_GROUND_TOLERANCE = config["mushroom"]["ground_tolerance"]

# Koopa Troopa enemy
KOOPA_TROOPA_SPEED = config["koopa_troopa"]["speed"]
KOOPA_TROOPA_GRAVITY = config["koopa_troopa"]["gravity"]
KOOPA_TROOPA_GROUND_TOLERANCE = config["koopa_troopa"]["ground_tolerance"]
KOOPA_TROOPA_ANIMATION_FPS = config["koopa_troopa"]["animation_fps"]
KOOPA_TROOPA_STOMP_BOUNCE_VELOCITY = config["koopa_troopa"]["stomp_bounce_velocity"]

# Koopa shell
KOOPA_SHELL_SPEED = config["koopa_shell"]["speed"]
KOOPA_SHELL_KICK_SPEED = config["koopa_shell"]["kick_speed"]
KOOPA_SHELL_GRAVITY = config["koopa_shell"]["gravity"]
KOOPA_SHELL_GROUND_TOLERANCE = config["koopa_shell"]["ground_tolerance"]
KOOPA_SHELL_STOMP_BOUNCE_VELOCITY = config["koopa_shell"]["stomp_bounce_velocity"]

# Entity knock-out (shell hits)
ENTITY_KNOCKOUT_VELOCITY_Y = config["entity_knockout"]["launch_velocity_y"]
ENTITY_KNOCKOUT_VELOCITY_X = config["entity_knockout"]["launch_velocity_x"]
