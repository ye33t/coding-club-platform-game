"""Tests for the GroundCollisionProcessor."""

import pytest

from game.constants import TILE_SIZE
from game.physics.ground_collision import GroundCollisionProcessor


class TestGroundCollisionProcessor:
    """Test ground collision detection and resolution."""

    def test_detects_ground_beneath_mario(self, level_with_ground, camera):
        """Should detect ground directly beneath Mario."""
        from game.mario import MarioIntent, MarioState
        from game.physics import PhysicsContext

        processor = GroundCollisionProcessor()
        state = MarioState(x=100, y=TILE_SIZE * 2 - 1, vy=-50)  # Just above ground
        context = PhysicsContext(
            state=state,
            intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_ground,
            camera=camera,
        )

        result = processor.process(context)

        assert result.state.on_ground
        assert result.state.vy == 0
        # Should be snapped to top of ground
        assert result.state.y == TILE_SIZE * 2

    def test_no_ground_when_in_air(self, empty_level, camera):
        """Should not detect ground when Mario is in the air."""
        from game.mario import MarioIntent, MarioState
        from game.physics import PhysicsContext

        processor = GroundCollisionProcessor()
        state = MarioState(x=100, y=100, vy=-50)  # High in the air
        context = PhysicsContext(
            state=state,
            intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        result = processor.process(context)

        assert not result.state.on_ground
        # Velocity should be unchanged
        assert result.state.vy == -50

    def test_detects_platform(self, level_with_platform, camera):
        """Should detect platform tiles as ground."""
        from game.mario import MarioIntent, MarioState
        from game.physics import PhysicsContext

        processor = GroundCollisionProcessor()
        # Mario above the platform at tile position 5
        state = MarioState(x=12 * TILE_SIZE, y=6 * TILE_SIZE - 1, vy=-50)
        context = PhysicsContext(
            state=state,
            intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_platform,
            camera=camera,
        )

        result = processor.process(context)

        assert result.state.on_ground
        assert result.state.vy == 0
        assert result.state.y == 6 * TILE_SIZE

    def test_only_applies_when_falling(self, level_with_ground, camera):
        """Ground collision should only apply when falling (vy <= 0)."""
        from game.mario import MarioIntent, MarioState
        from game.physics import PhysicsContext

        processor = GroundCollisionProcessor()
        # Mario moving upward through ground level
        state = MarioState(x=100, y=TILE_SIZE * 2 - 1, vy=100)  # Jumping up
        context = PhysicsContext(
            state=state,
            intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_ground,
            camera=camera,
        )

        result = processor.process(context)

        # Should not snap to ground when moving upward
        assert not result.state.on_ground
        assert result.state.vy == 100  # Velocity unchanged

    def test_samples_multiple_points(self, level_with_platform, camera):
        """Should sample left, center, and right of Mario."""
        from game.mario import MarioIntent, MarioState
        from game.physics import PhysicsContext

        processor = GroundCollisionProcessor()
        # Position Mario so only his right edge is over the platform
        state = MarioState(
            x=(10 * TILE_SIZE) - 8,  # Mostly off the platform
            y=6 * TILE_SIZE - 1,
            vy=-50,
        )
        context = PhysicsContext(
            state=state,
            intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_platform,
            camera=camera,
        )

        result = processor.process(context)

        # Should still detect ground from right edge sample
        assert result.state.on_ground
        assert result.state.y == 6 * TILE_SIZE
