"""Tests for death behavior processors."""

import pytest

from game.constants import TILE_SIZE
from game.mario import MarioIntent, MarioState
from game.physics import PhysicsContext, PhysicsPipeline
from game.physics.death_trigger import DeathTriggerProcessor
from game.physics.death_physics import DeathPhysicsProcessor
from game.physics.reset import ResetProcessor, RESET_THRESHOLD_Y


class TestDeathTriggerProcessor:
    """Test death trigger detection."""

    def test_triggers_death_when_below_screen(self, empty_level, camera):
        """Should trigger death when Mario falls below y=0."""
        processor = DeathTriggerProcessor()
        state = MarioState(x=100, y=-1, vy=-50)  # Below screen
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        result = processor.process(context)

        assert result.mario.is_dying
        assert result.mario.death_leap_velocity == 150.0
        assert result.mario.vy == 150.0  # Leap starts immediately
        assert not result.mario.on_ground

    def test_no_trigger_when_above_screen(self, empty_level, camera):
        """Should not trigger death when Mario is above y=0."""
        processor = DeathTriggerProcessor()
        state = MarioState(x=100, y=100, vy=-50)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        result = processor.process(context)

        assert not result.mario.is_dying
        assert result.mario.death_leap_velocity == 0.0

    def test_no_retrigger_when_already_dying(self, empty_level, camera):
        """Should not retrigger death if already dying."""
        processor = DeathTriggerProcessor()
        state = MarioState(x=100, y=-10, vy=-50, is_dying=True)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        original_vy = state.vy
        result = processor.process(context)

        # State should be unchanged
        assert result.mario.is_dying
        assert result.mario.vy == original_vy  # Not reset


class TestDeathPhysicsProcessor:
    """Test death physics handling."""

    def test_applies_gravity_when_dying(self, empty_level, camera):
        """Should apply gravity during death fall."""
        from game.physics.gravity import GRAVITY

        processor = DeathPhysicsProcessor()
        state = MarioState(x=100, y=50, vy=100, is_dying=True)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        result = processor.process(context)

        expected_vy = 100 - (GRAVITY * context.dt)
        assert result.mario.vy == pytest.approx(expected_vy)
        assert result.mario.vx == 0  # No horizontal movement
        assert not result.mario.on_ground

    def test_no_effect_when_not_dying(self, empty_level, camera):
        """Should not affect physics when not dying."""
        processor = DeathPhysicsProcessor()
        state = MarioState(x=100, y=50, vx=50, vy=100, is_dying=False)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        result = processor.process(context)

        # Velocities unchanged
        assert result.mario.vx == 50
        assert result.mario.vy == 100


class TestDeathIntegration:
    """Test complete death sequence in pipeline."""

    def test_full_death_sequence(self, empty_level, camera):
        """Test the complete death animation sequence."""
        pipeline = PhysicsPipeline()
        # Start Mario above screen, falling
        state = MarioState(x=100, y=10, vy=-100, on_ground=False)
        intent = MarioIntent(move_right=True)  # Input should be ignored when dying
        context = PhysicsContext(
            mario=state,
            mario_intent=intent,
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        # Process until Mario falls below screen
        for _ in range(30):  # More frames to ensure falling
            context = pipeline.process(context)
            if context.mario.y < 0:
                break

        # Should have triggered death
        assert context.mario.is_dying
        assert context.mario.action == "dying"

        # Should have initial upward velocity (death leap)
        assert context.mario.vy > 0

        # Process one more frame to ensure DeathPhysicsProcessor clears horizontal velocity
        context = pipeline.process(context)
        assert context.mario.vx == 0  # No horizontal movement during death

        # Continue processing death animation
        max_height = context.mario.y
        for _ in range(60):  # Process up to 1 second
            context = pipeline.process(context)
            max_height = max(max_height, context.mario.y)

        # Should have leaped up and fallen back down
        assert max_height > 0  # Jumped above trigger point
        assert context.mario.y < -50  # Fell well below screen

    def test_collisions_disabled_when_dying(self, level_with_platform, camera):
        """Collisions should be disabled during death."""
        pipeline = PhysicsPipeline()
        # Position Mario to collide with platform during death leap
        state = MarioState(
            x=12 * TILE_SIZE, y=-1, vy=-50, is_dying=False  # Just below screen
        )
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_platform,
            camera=camera,
        )

        # Trigger death
        context = pipeline.process(context)
        assert context.mario.is_dying

        # Continue processing - Mario should pass through platform
        for _ in range(30):
            context = pipeline.process(context)
            # Check if we're at platform height
            if 5 * TILE_SIZE <= context.mario.y <= 6 * TILE_SIZE:
                # Should pass through without collision
                assert context.mario.vx == 0
                # Velocity should only be affected by gravity, not collision
                assert context.mario.vy != 0

    def test_boundaries_ignored_when_dying(self, empty_level, camera):
        """Boundaries should not apply when dying."""
        pipeline = PhysicsPipeline()
        state = MarioState(x=100, y=-1, is_dying=True, vy=100)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        # Process death animation
        for _ in range(60):
            context = pipeline.process(context)

        # Should be allowed to fall far below screen (boundary not enforced)
        assert context.mario.y < -100  # Well below screen boundary


class TestResetProcessor:
    """Test reset trigger detection."""

    def test_triggers_reset_when_fallen_far_enough(self, empty_level, camera):
        """Should trigger reset when dying Mario falls below threshold."""
        processor = ResetProcessor()
        state = MarioState(x=100, y=RESET_THRESHOLD_Y - 1, is_dying=True)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        result = processor.process(context)

        assert result.mario.should_reset

    def test_no_reset_above_threshold(self, empty_level, camera):
        """Should not trigger reset when above threshold."""
        processor = ResetProcessor()
        state = MarioState(x=100, y=RESET_THRESHOLD_Y + 1, is_dying=True)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        result = processor.process(context)

        assert not result.mario.should_reset

    def test_no_reset_when_not_dying(self, empty_level, camera):
        """Should not trigger reset if not dying."""
        processor = ResetProcessor()
        state = MarioState(x=100, y=RESET_THRESHOLD_Y - 1, is_dying=False)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        result = processor.process(context)

        assert not result.mario.should_reset


class TestResetIntegration:
    """Test complete death-reset cycle."""

    def test_full_death_and_reset_cycle(self, empty_level, camera):
        """Test the complete death animation and reset trigger."""
        pipeline = PhysicsPipeline()
        # Start Mario falling
        state = MarioState(x=100, y=10, vy=-100, on_ground=False)
        context = PhysicsContext(
            mario=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera=camera,
        )

        # Process until Mario dies
        for _ in range(30):
            context = pipeline.process(context)
            if context.mario.is_dying:
                break

        assert context.mario.is_dying
        assert not context.mario.should_reset  # Not yet

        # Continue processing until reset triggers
        for _ in range(200):  # Enough frames to fall below threshold
            context = pipeline.process(context)
            if context.mario.should_reset:
                break

        # Should have triggered reset
        assert context.mario.should_reset
        assert context.mario.y < RESET_THRESHOLD_Y

    def test_camera_resets_properly(self, empty_level):
        """Test that camera resets to origin when Mario respawns."""
        from game.world import World
        from game.mario import Mario, MarioState
        import pygame

        world = World()
        mario = Mario(MarioState(x=200, y=10))

        # Move camera forward
        world.camera.update(200, world.level.width_pixels)
        assert world.camera.x > 0
        assert world.camera.max_x > 0

        # Create mock key state
        keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_LSHIFT: False,
            pygame.K_SPACE: False,
            pygame.K_DOWN: False,
        }

        # Simulate death and reset
        mario.state.should_reset = True
        world.update(mario, keys, 1/60)

        # Camera should be back at origin
        assert world.camera.x == 0
        assert world.camera.max_x == 0
        # Mario should be at starting position
        assert mario.state.x == 50.0
        assert mario.state.y == 16.0
