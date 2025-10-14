"""Render layer for drawables positioned behind terrain."""

from __future__ import annotations

from .base import RenderContext, RenderLayer


class BehindDrawablesLayer(RenderLayer):
    """Draws drawables positioned behind terrain."""

    def draw(
        self,
        context: RenderContext,
    ) -> None:
        for drawable in context.behind_drawables:
            drawable.draw(context.surface, context.camera)
