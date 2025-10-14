"""Render layer for drawables positioned at or above terrain."""

from __future__ import annotations

from .base import RenderContext, RenderLayer


class FrontDrawablesLayer(RenderLayer):
    """Draws drawables positioned at or above terrain."""

    def draw(
        self,
        context: RenderContext,
    ) -> None:
        for drawable in context.front_drawables:
            drawable.draw(context.surface, context.camera)
