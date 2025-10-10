"""Processors for handling Mario power-up transitions."""

from __future__ import annotations

from .base import PhysicsContext, PhysicsProcessor


class PowerUpTransitionProcessor(PhysicsProcessor):
    """Manage temporal transitions triggered by power-up collection."""

    TOGGLE_INTERVAL = 0.1  # Seconds between size toggles during small->big anim

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Advance any active power-up animations."""
        mario_state = context.mario_state

        if mario_state.power_up_transition == "small_to_big":
            self._process_small_to_big_transition(context)

        return context

    def _process_small_to_big_transition(self, context: PhysicsContext) -> None:
        """Animate Mario toggling between small and big sizes."""
        mario_state = context.mario_state

        mario_state.transition_time_remaining -= context.dt
        mario_state.transition_toggle_timer += context.dt

        while mario_state.transition_toggle_timer >= self.TOGGLE_INTERVAL:
            mario_state.transition_toggle_timer -= self.TOGGLE_INTERVAL
            mario_state.transition_show_target = not mario_state.transition_show_target
            self._apply_transition_size(mario_state)

        if mario_state.transition_time_remaining <= 0:
            mario_state.set_size(mario_state.transition_to_size or "big")
            mario_state.power_up_transition = None
            mario_state.transition_from_size = None
            mario_state.transition_to_size = None
            mario_state.transition_time_remaining = 0.0
            mario_state.transition_toggle_timer = 0.0
            mario_state.transition_show_target = True

    def _apply_transition_size(self, mario_state) -> None:
        """Toggle Mario between source and target sizes."""
        if mario_state.transition_show_target:
            size = mario_state.transition_to_size or mario_state.size
        else:
            size = mario_state.transition_from_size or mario_state.size

        mario_state.set_size(size)
