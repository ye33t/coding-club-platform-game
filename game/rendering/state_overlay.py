"""Render layer that delegates to the active state's overlay hook."""

from __future__ import annotations

from .base import RenderContext, RenderLayer


class StateOverlayLayer(RenderLayer):
    """Ask the active state to draw a full-screen overlay if desired."""

    def __init__(self, hud_layer: RenderLayer) -> None:
        self._hud_layer = hud_layer

    def draw(self, context: RenderContext) -> None:
        from ..states.base import State as BaseState

        state = context.game.state
        has_overlay = type(state).draw_overlay is not BaseState.draw_overlay

        if has_overlay:
            state.draw_overlay(context.game, context)

        self._hud_layer.draw(context)
