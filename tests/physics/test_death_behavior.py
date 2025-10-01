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
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        result = processor.process(context)

        assert result.mario_state.is_dying
        assert result.mario_state.death_leap_velocity == 150.0
        assert result.mario_state.vy == 150.0  # Leap starts immediately
        assert not result.mario_state.on_ground

    def test_no_trigger_when_above_screen(self, empty_level, camera):
        """Should not trigger death when Mario is above y=0."""
        processor = DeathTriggerProcessor()
        state = MarioState(x=100, y=100, vy=-50)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        result = processor.process(context)

        assert not result.mario_state.is_dying
        assert result.mario_state.death_leap_velocity == 0.0

    def test_no_retrigger_when_already_dying(self, empty_level, camera):
        """Should not retrigger death if already dying."""
        processor = DeathTriggerProcessor()
        state = MarioState(x=100, y=-10, vy=-50, is_dying=True)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        original_vy = state.vy
        result = processor.process(context)

        # State should be unchanged
        assert result.mario_state.is_dying
        assert result.mario_state.vy == original_vy  # Not reset


class TestDeathPhysicsProcessor:
    """Test death physics handling."""

    def test_applies_gravity_when_dying(self, empty_level, camera):
        """Should apply gravity during death fall."""
        from game.physics.gravity import GRAVITY

        processor = DeathPhysicsProcessor()
        state = MarioState(x=100, y=50, vy=100, is_dying=True)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        result = processor.process(context)

        expected_vy = 100 - (GRAVITY * context.dt)
        assert result.mario_state.vy == pytest.approx(expected_vy)
        assert result.mario_state.vx == 0  # No horizontal movement
        assert not result.mario_state.on_ground

    def test_no_effect_when_not_dying(self, empty_level, camera):
        """Should not affect physics when not dying."""
        processor = DeathPhysicsProcessor()
        state = MarioState(x=100, y=50, vx=50, vy=100, is_dying=False)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        result = processor.process(context)

        # Velocities unchanged
        assert result.mario_state.vx == 50
        assert result.mario_state.vy == 100


class TestDeathIntegration:
    """Test complete death sequence in pipeline."""

    def test_full_death_sequence(self, empty_level, camera):
        """Test the complete death animation sequence."""
        pipeline = PhysicsPipeline()
        # Start Mario above screen, falling
        state = MarioState(x=100, y=10, vy=-100, on_ground=False)
        intent = MarioIntent(move_right=True)  # Input should be ignored when dying
        context = PhysicsContext(
            mario_state=state,
            mario_intent=intent,
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        # Process until Mario falls below screen
        for _ in range(30):  # More frames to ensure falling
            context = pipeline.process(context)
            if context.mario_state.y < 0:
                break

        # Should have triggered death
        assert context.mario_state.is_dying
        assert context.mario_state.action == "dying"

        # Should have initial upward velocity (death leap)
        assert context.mario_state.vy > 0

        # Process one more frame to ensure DeathPhysicsProcessor clears horizontal velocity
        context = pipeline.process(context)
        assert context.mario_state.vx == 0  # No horizontal movement during death

        # Continue processing death animation
        max_height = context.mario_state.y
        for _ in range(60):  # Process up to 1 second
            context = pipeline.process(context)
            max_height = max(max_height, context.mario_state.y)

        # Should have leaped up and fallen back down
        assert max_height > 0  # Jumped above trigger point
        assert context.mario_state.y < -50  # Fell well below screen

    def test_collisions_disabled_when_dying(self, level_with_platform, camera):
        """Collisions should be disabled during death."""
        pipeline = PhysicsPipeline()
        # Position Mario to collide with platform during death leap
        state = MarioState(
            x=6 * TILE_SIZE, y=-1, vy=-50, is_dying=False  # Just below screen
        )
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=level_with_platform,
            camera_state=camera.state,
        )

        # Trigger death
        context = pipeline.process(context)
        assert context.mario_state.is_dying

        # Continue processing - Mario should pass through platform
        for _ in range(30):
            context = pipeline.process(context)
            # Check if we're at platform height
            if 2 * TILE_SIZE <= context.mario_state.y <= 3 * TILE_SIZE:
                # Should pass through without collision
                assert context.mario_state.vx == 0
                # Velocity should only be affected by gravity, not collision
                assert context.mario_state.vy != 0

    def test_boundaries_ignored_when_dying(self, empty_level, camera):
        """Boundaries should not apply when dying."""
        pipeline = PhysicsPipeline()
        state = MarioState(x=100, y=-1, is_dying=True, vy=100)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        # Process death animation
        for _ in range(60):
            context = pipeline.process(context)

        # Should be allowed to fall far below screen (boundary not enforced)
        assert context.mario_state.y < -100  # Well below screen boundary


class TestResetProcessor:
    """Test reset trigger detection."""

    def test_triggers_reset_when_fallen_far_enough(self, empty_level, camera):
        """Should reset Mario when dying Mario falls below threshold."""
        processor = ResetProcessor()
        state = MarioState(x=100, y=RESET_THRESHOLD_Y - 1, is_dying=True)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        result = processor.process(context)

        # Should have reset Mario to level's spawn position
        assert result.mario_state.x == empty_level.spawn_x
        assert result.mario_state.y == empty_level.spawn_y
        assert not result.mario_state.is_dying
        # Should have reset camera
        assert result.camera_state.x == 0
        assert result.camera_state.max_x == 0

    def test_no_reset_above_threshold(self, empty_level, camera):
        """Should not trigger reset when above threshold."""
        processor = ResetProcessor()
        state = MarioState(x=100, y=RESET_THRESHOLD_Y + 1, is_dying=True)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        result = processor.process(context)

        # Should not have reset - Mario still at original position
        assert result.mario_state.x == 100
        assert result.mario_state.y == RESET_THRESHOLD_Y + 1
        assert result.mario_state.is_dying

    def test_no_reset_when_not_dying(self, empty_level, camera):
        """Should not trigger reset if not dying."""
        processor = ResetProcessor()
        state = MarioState(x=100, y=RESET_THRESHOLD_Y - 1, is_dying=False)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        result = processor.process(context)

        # Should not have reset - Mario still at original position
        assert result.mario_state.x == 100
        assert result.mario_state.y == RESET_THRESHOLD_Y - 1
        assert not result.mario_state.is_dying


class TestResetIntegration:
    """Test complete death-reset cycle."""

    def test_full_death_and_reset_cycle(self, empty_level, camera):
        """Test the complete death animation and reset trigger."""
        pipeline = PhysicsPipeline()
        # Start Mario falling
        state = MarioState(x=100, y=10, vy=-100, on_ground=False)
        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1 / 60,
            level=empty_level,
            camera_state=camera.state,
        )

        # Process until Mario dies
        for _ in range(30):
            context = pipeline.process(context)
            if context.mario_state.is_dying:
                break

        assert context.mario_state.is_dying

        # Continue processing until reset happens
        for _ in range(200):  # Enough frames to fall below threshold
            prev_y = context.mario_state.y
            context = pipeline.process(context)
            # Check if reset happened (Mario back at start)
            if context.mario_state.x == empty_level.spawn_x and context.mario_state.y == empty_level.spawn_y:
                break

        # Should have reset
        assert context.mario_state.x == empty_level.spawn_x
        assert context.mario_state.y == empty_level.spawn_y
        assert not context.mario_state.is_dying

    def test_camera_resets_properly(self, level_with_ground):
        """Test that camera resets to origin when Mario respawns."""
        from game.physics import PhysicsPipeline
        from game.camera import Camera

        pipeline = PhysicsPipeline()

        # Position Mario below death threshold while dying, with camera moved forward
        state = MarioState(x=400, y=RESET_THRESHOLD_Y - 1, is_dying=True)
        camera = Camera()
        # Manually move camera forward (simulating prior movement)
        camera.state.x = 100
        camera.state.max_x = 100

        context = PhysicsContext(
            mario_state=state,
            mario_intent=MarioIntent(),
            dt=1/60,
            level=level_with_ground,  # This has width_tiles = 32 (512 pixels)
            camera_state=camera.state,
        )

        # Verify camera has been moved
        assert context.camera_state.x > 0
        assert context.camera_state.max_x > 0

        # Process through pipeline which should trigger reset
        result = pipeline.process(context)

        # Camera should be back at origin
        assert result.camera_state.x == 0
        assert result.camera_state.max_x == 0
        # Mario should be at starting position (spawn point)
        assert result.mario_state.x == level_with_ground.spawn_x
        assert result.mario_state.y == level_with_ground.spawn_y
        assert not result.mario_state.is_dying
