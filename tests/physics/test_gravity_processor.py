"""Tests for the GravityProcessor."""

import pytest

from game.physics.gravity import GRAVITY, JUMP_VELOCITY, GravityProcessor


class TestGravityProcessor:
    """Test gravity and jumping physics."""

    def test_gravity_applies_when_not_on_ground(self, basic_context):
        """Gravity should pull Mario down when in air."""
        processor = GravityProcessor()
        basic_context.mario_state.on_ground = False
        basic_context.mario_state.vy = 0

        result = processor.process(basic_context)

        # Gravity pulls down (negative velocity)
        expected_vy = -GRAVITY * basic_context.dt
        assert result.mario_state.vy == pytest.approx(expected_vy)

    def test_no_gravity_when_on_ground(self, basic_context):
        """Gravity should not apply when Mario is on ground."""
        processor = GravityProcessor()
        basic_context.mario_state.on_ground = True
        basic_context.mario_state.vy = 0

        result = processor.process(basic_context)

        # Velocity should remain unchanged
        assert result.mario_state.vy == 0

    def test_jump_initiates_when_on_ground(self, basic_context):
        """Jump should give upward velocity when on ground."""
        processor = GravityProcessor()
        basic_context.mario_state.on_ground = True
        basic_context.mario_state.vy = 0
        basic_context.mario_intent.jump = True

        result = processor.process(basic_context)

        # Should have jump velocity (gravity also applied in same frame)
        expected_vy = JUMP_VELOCITY - (GRAVITY * basic_context.dt)
        assert result.mario_state.vy == pytest.approx(expected_vy)
        assert not result.mario_state.on_ground

    def test_no_jump_when_in_air(self, basic_context):
        """Can't jump when already in the air."""
        processor = GravityProcessor()
        basic_context.mario_state.on_ground = False
        basic_context.mario_state.vy = -50  # Falling
        basic_context.mario_intent.jump = True

        result = processor.process(basic_context)

        # Velocity should only be affected by gravity, not jump
        expected_vy = -50 - (GRAVITY * basic_context.dt)
        assert result.mario_state.vy == pytest.approx(expected_vy)
        assert not result.mario_state.on_ground

    def test_gravity_accumulates_over_time(self, basic_context):
        """Gravity should make Mario fall faster over time."""
        processor = GravityProcessor()
        basic_context.mario_state.on_ground = False
        basic_context.mario_state.vy = 0

        # Process multiple frames
        velocities = [0.0]
        context = basic_context
        for _ in range(5):
            context = processor.process(context)
            velocities.append(context.mario_state.vy)

        # Each velocity should be more negative than the last
        for i in range(1, len(velocities)):
            assert velocities[i] < velocities[i - 1]
