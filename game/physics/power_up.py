"""Processors for handling Mario power-up transitions."""

from __future__ import annotations

from .base import PhysicsContext, PhysicsProcessor


class PowerUpTransitionProcessor(PhysicsProcessor):
    """Manage temporal transitions triggered by power-up collection."""

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Advance any active power-up animations."""
        mario_state = context.mario_state

        if mario_state.power_up_transition == "small_to_big":
            self._process_small_to_big_transition(context.dt, mario_state)

        return context

    def _process_small_to_big_transition(self, dt: float, mario_state) -> None:
        """Animate Mario toggling between small and big sizes every other frame."""
        mario_state.transition_time_remaining -= dt

        if mario_state.transition_time_remaining > 0:
            mario_state.transition_toggle_counter += 1
            if mario_state.transition_toggle_counter >= 2:
                mario_state.transition_toggle_counter = 0
                mario_state.transition_show_target = not mario_state.transition_show_target
                self._apply_transition_size(mario_state)
        else:
            mario_state.transition_show_target = True
            mario_state.set_size(mario_state.transition_to_size or mario_state.size)
            mario_state.power_up_transition = None
            mario_state.transition_from_size = None
            mario_state.transition_to_size = None
            mario_state.transition_time_remaining = 0.0
            mario_state.transition_toggle_counter = 0

    def _apply_transition_size(self, mario_state) -> None:
        """Toggle Mario between source and target sizes."""
        if mario_state.transition_show_target:
            size = mario_state.transition_to_size or mario_state.size
        else:
            size = mario_state.transition_from_size or mario_state.size

        mario_state.set_size(size)
