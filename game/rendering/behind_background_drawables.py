"""Render layer for drawables positioned behind terrain."""

from __future__ import annotations

from .base import RenderContext, RenderLayer


class BehindBackgroundDrawablesLayer(RenderLayer):
    """Draws drawables positioned behind the background."""

    def draw(
        self,
        context: RenderContext,
    ) -> None:
        for drawable in context.behind_background_drawables:
            drawable.draw(context.surface, context.camera)
