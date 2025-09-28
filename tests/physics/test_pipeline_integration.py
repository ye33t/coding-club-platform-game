"""Integration tests for the complete physics pipeline."""

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
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        # Process multiple frames to see falling
        for _ in range(3):
            context = pipeline.process(context)

        # Mario should have fallen
        assert context.mario.y < initial_y
        assert context.mario.vy < 0  # Falling velocity
        assert not context.mario.on_ground
        assert context.mario.action == "jumping"  # In air

    def test_mario_lands_on_ground(self, level_with_ground, camera):
        """Mario should stop falling when hitting ground."""
        pipeline = PhysicsPipeline()
        state = MarioState(x=100, y=TILE_SIZE * 3, vy=-100)  # Falling fast
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_ground,
            camera=camera,
        )

        # Process until Mario lands
        for _ in range(10):
            context = pipeline.process(context)
            if context.mario.on_ground:
                break

        # Should be on ground
        assert context.mario.on_ground
        assert context.mario.vy == 0
        assert context.mario.y == TILE_SIZE * 2  # Top of ground
        assert context.mario.action == "idle"

    def test_complete_jump_cycle(self, level_with_ground, camera):
        """Test a complete jump from ground back to ground."""
        pipeline = PhysicsPipeline()
        state = MarioState(x=100, y=TILE_SIZE * 2, on_ground=True)
        intent = MarioIntent(jump=True)
        context = PhysicsContext(
            mario=state,
            mario_intent=intent,
            dt=1 / 60,
            level=level_with_ground,
            camera=camera,
        )

        # Initial jump
        context = pipeline.process(context)
        assert context.mario.vy > 0  # Moving up
        assert not context.mario.on_ground
        max_height = context.mario.y

        # Continue jumping for a few frames
        for _ in range(5):
            context = pipeline.process(context)
            max_height = max(max_height, context.mario.y)

        # Stop jumping and let Mario fall
        context.mario_intent.jump = False
        for _ in range(60):  # Process up to 1 second
            context = pipeline.process(context)
            if context.mario.on_ground:
                break

        # Should be back on ground
        assert context.mario.on_ground
        assert context.mario.y == TILE_SIZE * 2
        assert max_height > TILE_SIZE * 2  # Did go up

    def test_horizontal_movement_with_friction(self, level_with_ground, camera):
        """Test moving right then stopping with friction."""
        pipeline = PhysicsPipeline()
        state = MarioState(x=100, y=TILE_SIZE * 2, on_ground=True)
        intent = MarioIntent(move_right=True)
        context = PhysicsContext(
            mario=state,
            mario_intent=intent,
            dt=1 / 60,
            level=level_with_ground,
            camera=camera,
        )

        # Move right for a few frames
        for _ in range(5):
            context = pipeline.process(context)

        assert context.mario.x > 100  # Moved right
        assert context.mario.vx > 0  # Moving right
        assert context.mario.action == "walking"

        # Stop moving and let friction slow Mario
        context.mario_intent.move_right = False
        initial_vx = context.mario.vx

        for _ in range(30):
            context = pipeline.process(context)
            if context.mario.vx == 0:
                break

        # Should have stopped
        assert context.mario.vx == 0
        assert context.mario.action == "idle"

    def test_wall_blocks_movement(self, level_with_platform, camera):
        """Walls should block horizontal movement."""
        pipeline = PhysicsPipeline()
        # Position Mario to the left of the platform, at platform height
        # Make sure he's on ground so he doesn't fall
        state = MarioState(
            x=(10 * TILE_SIZE) - 20,  # Just left of platform
            y=5 * TILE_SIZE,  # Exactly at platform height
            on_ground=True,  # Start on ground to avoid falling
            vx=0,
        )
        intent = MarioIntent(move_right=True)
        context = PhysicsContext(
            mario=state,
            mario_intent=intent,
            dt=1 / 60,
            level=level_with_platform,
            camera=camera,
        )

        # Try to move into the wall for several frames
        for _ in range(5):
            context = pipeline.process(context)

        # Should be stopped at wall edge
        assert context.mario.x < 10 * TILE_SIZE  # Can't pass through wall
        # Check that we're close to the wall (within Mario's width)
        assert context.mario.x >= (10 * TILE_SIZE) - context.mario.width - 1

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
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_platform,
            camera=camera,
        )

        # Process until Mario would hit ceiling
        max_y = state.y
        for _ in range(10):
            context = pipeline.process(context)
            if context.mario.vy <= 0:  # Hit ceiling and falling
                break
            max_y = max(max_y, context.mario.y)

        # Should have hit ceiling and stopped upward movement
        assert context.mario.vy <= 0  # No longer moving up
        assert max_y < 5 * TILE_SIZE  # Didn't pass through platform
