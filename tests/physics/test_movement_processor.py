"""Tests for the MovementProcessor."""

import pytest

from game.physics.movement import FRICTION, MovementProcessor


class TestMovementProcessor:
    """Test horizontal movement and friction physics."""

    def test_friction_applies_when_no_input(self, basic_context):
        """Friction should slow Mario when no movement intent."""
        processor = MovementProcessor()
        basic_context.state.vx = 100.0  # Moving right
        basic_context.intent.move_left = False
        basic_context.intent.move_right = False

        result = processor.process(basic_context)

        # Should be slowed by friction
        expected_vx = 100.0 * FRICTION
        assert result.state.vx == pytest.approx(expected_vx)

    def test_no_friction_when_moving(self, basic_context):
        """Friction should not apply when player is actively moving."""
        processor = MovementProcessor()
        basic_context.state.vx = 100.0
        basic_context.intent.move_right = True

        result = processor.process(basic_context)

        # Velocity should be unchanged (IntentProcessor handles acceleration)
        assert result.state.vx == 100.0

    def test_stops_at_low_velocity(self, basic_context):
        """Should stop completely when velocity is very small."""
        processor = MovementProcessor()
        basic_context.state.vx = 0.5  # Very slow
        basic_context.intent.move_left = False
        basic_context.intent.move_right = False

        result = processor.process(basic_context)

        # Should be stopped completely
        assert result.state.vx == 0.0

    def test_friction_works_both_directions(self, basic_context):
        """Friction should work for both left and right movement."""
        processor = MovementProcessor()

        # Test moving right
        basic_context.state.vx = 100.0
        basic_context.intent.move_left = False
        basic_context.intent.move_right = False
        result = processor.process(basic_context)
        assert 0 < result.state.vx < 100.0

        # Test moving left
        basic_context.state.vx = -100.0
        result = processor.process(basic_context)
        assert -100.0 < result.state.vx < 0

    def test_friction_applied_multiple_times(self, basic_context):
        """Friction should compound over multiple frames."""
        processor = MovementProcessor()
        basic_context.state.vx = 100.0
        basic_context.intent.move_left = False
        basic_context.intent.move_right = False

        # Apply friction multiple times
        context = basic_context
        for _ in range(3):
            context = processor.process(context)

        # Should be significantly slower
        expected_vx = 100.0 * (FRICTION**3)
        assert context.state.vx == pytest.approx(expected_vx)
