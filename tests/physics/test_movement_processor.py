"""Tests for the MovementProcessor."""

import pytest

from game.physics.movement import MIN_FRICTION, MAX_FRICTION, MovementProcessor


class TestMovementProcessor:
    """Test horizontal movement and friction physics."""

    def test_friction_applies_when_no_input(self, basic_context):
        """Friction should slow Mario when no movement intent."""
        processor = MovementProcessor()
        basic_context.mario_state.vx = 100.0  # Moving right (high speed)
        basic_context.mario_intent.move_left = False
        basic_context.mario_intent.move_right = False

        result = processor.process(basic_context)

        # At high speed (100), friction should be MIN_FRICTION
        expected_vx = 100.0 * MIN_FRICTION
        assert result.mario_state.vx == pytest.approx(expected_vx)

    def test_no_friction_when_moving(self, basic_context):
        """Friction should not apply when player is actively moving."""
        processor = MovementProcessor()
        basic_context.mario_state.vx = 100.0
        basic_context.mario_intent.move_right = True

        result = processor.process(basic_context)

        # Velocity should be unchanged (IntentProcessor handles acceleration)
        assert result.mario_state.vx == 100.0

    def test_stops_at_low_velocity(self, basic_context):
        """Should stop completely when velocity is very small."""
        processor = MovementProcessor()
        basic_context.mario_state.vx = 0.5  # Very slow
        basic_context.mario_intent.move_left = False
        basic_context.mario_intent.move_right = False

        result = processor.process(basic_context)

        # Should be stopped completely
        assert result.mario_state.vx == 0.0

    def test_friction_works_both_directions(self, basic_context):
        """Friction should work for both left and right movement."""
        processor = MovementProcessor()

        # Test moving right
        basic_context.mario_state.vx = 100.0
        basic_context.mario_intent.move_left = False
        basic_context.mario_intent.move_right = False
        result = processor.process(basic_context)
        assert 0 < result.mario_state.vx < 100.0

        # Test moving left
        basic_context.mario_state.vx = -100.0
        result = processor.process(basic_context)
        assert -100.0 < result.mario_state.vx < 0

    def test_friction_applied_multiple_times(self, basic_context):
        """Friction should compound over multiple frames."""
        processor = MovementProcessor()
        basic_context.mario_state.vx = 100.0  # High speed
        basic_context.mario_intent.move_left = False
        basic_context.mario_intent.move_right = False

        # Apply friction multiple times
        context = basic_context
        for _ in range(3):
            context = processor.process(context)

        # Should be significantly slower but exact value depends on velocity-based friction
        # Starting at 100, should end up around 65-70 after 3 frames
        assert 65.0 < context.mario_state.vx < 70.0

    def test_velocity_based_friction(self, basic_context):
        """Friction should vary based on velocity."""
        processor = MovementProcessor()
        basic_context.mario_intent.move_left = False
        basic_context.mario_intent.move_right = False

        # Test low speed - should have high friction (quick stop)
        basic_context.mario_state.vx = 15.0
        result = processor.process(basic_context)
        # At low speeds, friction should be closer to MAX_FRICTION
        assert result.mario_state.vx < 15.0 * 0.70  # Should drop significantly

        # Test high speed - should have low friction (more sliding)
        basic_context.mario_state.vx = 100.0
        result = processor.process(basic_context)
        # At high speeds, friction should be MIN_FRICTION
        assert result.mario_state.vx == pytest.approx(100.0 * MIN_FRICTION)
