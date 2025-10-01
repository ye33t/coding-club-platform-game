"""Integration tests for the complete physics pipeline."""

import math
import pytest

from game.constants import TILE_SIZE
from game.mario import MarioIntent, MarioState
from game.physics import PhysicsContext, PhysicsPipeline


class TestPhysicsPipeline:
    """Test the complete physics pipeline with real scenarios."""

    def test_mario_falls_with_gravity(self, empty_level, camera):
        """Mario should fall when there's no ground beneath."""
        pipeline = PhysicsPipeline()
        initial_y = 100.0
        state = MarioState(x=100, y=initial_y, vy=0)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        # Process multiple frames to see falling
        for _ in range(3):
            context = pipeline.process(context)

        # Mario should have fallen
        assert context.mario_state.y < initial_y
        assert context.mario_state.vy < 0  # Falling velocity
        assert not context.mario_state.on_ground
        assert context.mario_state.action == "jumping"  # In air

    def test_mario_lands_on_ground(self, level_with_ground, camera):
        """Mario should stop falling when hitting ground."""
        pipeline = PhysicsPipeline()
        state = MarioState(x=100, y=TILE_SIZE * 3, vy=-100)  # Falling fast
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_ground,
            camera_state=camera.state,
        )

        # Process until Mario lands
        for _ in range(10):
            context = pipeline.process(context)
            if context.mario_state.on_ground:
                break

        # Should be on ground
        assert context.mario_state.on_ground
        assert context.mario_state.vy == 0
        assert context.mario_state.y == TILE_SIZE * 2  # Top of ground
        assert context.mario_state.action == "idle"

    def test_complete_jump_cycle(self, level_with_ground, camera):
        """Test a complete jump from ground back to ground."""
        pipeline = PhysicsPipeline()
        state = MarioState(x=100, y=TILE_SIZE * 2, on_ground=True)
        intent = MarioIntent(jump=True)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=intent,
            dt=1 / 60,
            level=level_with_ground,
            camera_state=camera.state,
        )

        # Initial jump
        context = pipeline.process(context)
        assert context.mario_state.vy > 0  # Moving up
        assert not context.mario_state.on_ground
        max_height = context.mario_state.y

        # Continue jumping for a few frames
        for _ in range(5):
            context = pipeline.process(context)
            max_height = max(max_height, context.mario_state.y)

        # Stop jumping and let Mario fall
        context.mario_intent.jump = False
        for _ in range(60):  # Process up to 1 second
            context = pipeline.process(context)
            if context.mario_state.on_ground:
                break

        # Should be back on ground
        assert context.mario_state.on_ground
        assert context.mario_state.y == TILE_SIZE * 2
        assert max_height > TILE_SIZE * 2  # Did go up

    def test_horizontal_movement_with_friction(self, level_with_ground, camera):
        """Test moving right then stopping with friction."""
        pipeline = PhysicsPipeline()
        state = MarioState(x=100, y=TILE_SIZE * 2, on_ground=True)
        intent = MarioIntent(move_right=True)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=intent,
            dt=1 / 60,
            level=level_with_ground,
            camera_state=camera.state,
        )

        # Move right for a few frames
        for _ in range(10):
            context = pipeline.process(context)

        assert context.mario_state.x > 100  # Moved right
        assert context.mario_state.vx > 0  # Moving right
        assert context.mario_state.action == "walking"

        # Stop moving and let friction slow Mario
        context.mario_intent.move_right = False

        for _ in range(30):
            context = pipeline.process(context)
            if context.mario_state.vx == 0:
                break

        # Should have stopped
        assert context.mario_state.vx == 0
        assert context.mario_state.action == "idle"

    def test_wall_blocks_movement(self, empty_level, camera):
        """Walls should block horizontal movement."""
        from game.tile_definitions import TILE_GROUND

        pipeline = PhysicsPipeline()
        # Create a wall at ground level
        # Add ground and a wall
        for x in range(empty_level.width_tiles):
            empty_level.tiles[0][0][x] = TILE_GROUND
            empty_level.tiles[0][1][x] = TILE_GROUND
        # Add a vertical wall at x=10
        for y in range(2, 6):
            empty_level.tiles[0][y][10] = TILE_GROUND

        # Position Mario to the left of the wall, on ground
        state = MarioState(
            x=(10 * TILE_SIZE) - 20,  # Just left of wall
            y=2 * TILE_SIZE,  # On ground
            on_ground=True,
            vx=0,
        )
        intent = MarioIntent(move_right=True)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=intent,
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        # Try to move into the wall for more frames to ensure we reach it
        for _ in range(20):
            context = pipeline.process(context)

        # Should be stopped at wall edge
        # Mario's right edge should be at the wall (x=160)
        # So Mario's x should be 160 - 16 = 144
        assert math.isclose(context.mario_state.x, (10 * TILE_SIZE) - context.mario_state.width, abs_tol=1.0)
        assert math.isclose(context.mario_state.x, (10 * TILE_SIZE) - context.mario_state.width, abs_tol=1.0)

    def test_ceiling_collision(self, level_with_platform, camera):
        """Mario should hit ceiling when jumping into platform from below."""
        pipeline = PhysicsPipeline()
        # Position Mario below the platform
        state = MarioState(
            x=12 * TILE_SIZE,  # Under platform
            y=3 * TILE_SIZE,
            vy=200,  # Jumping up fast
            on_ground=False,
        )
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_platform,
            camera_state=camera.state,
        )

        # Process until Mario would hit ceiling
        max_y = state.y
        for _ in range(10):
            context = pipeline.process(context)
            if context.mario_state.vy <= 0:  # Hit ceiling and falling
                break
            max_y = max(max_y, context.mario_state.y)

        # Should have hit ceiling and stopped upward movement
        assert context.mario_state.vy <= 0  # No longer moving up
        assert max_y < 5 * TILE_SIZE  # Didn't pass through platform
