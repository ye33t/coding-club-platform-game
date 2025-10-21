"""Detect collection of terrain coins and award HUD updates."""

from __future__ import annotations

from typing import Iterable, Tuple

from ..constants import TILE_SIZE
from ..content.tile_definitions import empty_tile_slug
from ..effects.coin import CoinEffect
from ..gameplay import HUD_COIN_INCREMENT
from .base import PhysicsContext, PhysicsProcessor
from .events import CollectCoinEvent, SpawnEffectEvent, TerrainTileChangeEvent


class CollectableCollisionProcessor(PhysicsProcessor):
    """Detect intersecting collectable tiles and convert them into coin rewards."""

    _COLLECTABLE_CATEGORY = "collectable"

    def process(self, context: PhysicsContext) -> PhysicsContext:
        mario = context.mario
        level = context.level
        empty_slug = empty_tile_slug()

        collected_tiles = list(
            self._collect_tiles_touching_mario(
                level_width=level.width_tiles,
                level_height=level.height_tiles,
                tile_lookup=lambda x, y: level.get_terrain_tile(mario.screen, x, y),
                definition_lookup=level.get_tile_definition,
                mario_bounds=(
                    mario.x,
                    mario.y,
                    mario.x + mario.width,
                    mario.y + mario.height,
                ),
                empty_slug=empty_slug,
            )
        )

        if not collected_tiles:
            return context

        coins_collected = len(collected_tiles) * HUD_COIN_INCREMENT
        context.add_event(CollectCoinEvent(amount=coins_collected))

        for tile_x, tile_y in collected_tiles:
            context.add_event(
                TerrainTileChangeEvent(
                    screen=mario.screen,
                    x=tile_x,
                    y=tile_y,
                    slug=empty_slug,
                )
            )
            world_x = tile_x * TILE_SIZE
            world_y = (tile_y + 1) * TILE_SIZE
            context.add_event(
                SpawnEffectEvent(
                    effect=CoinEffect(
                        world_x=world_x,
                        world_y=world_y,
                    )
                )
            )

        return context

    def _collect_tiles_touching_mario(
        self,
        *,
        level_width: int,
        level_height: int,
        tile_lookup,
        definition_lookup,
        mario_bounds: Tuple[float, float, float, float],
        empty_slug: str,
    ) -> Iterable[Tuple[int, int]]:
        """Yield collectable tile coordinates overlapping Mario's bounds."""
        left, bottom, right, top = mario_bounds

        tile_left = max(int(left // TILE_SIZE), 0)
        tile_right = min(int((right - 1) // TILE_SIZE), max(level_width - 1, 0))
        tile_bottom = max(int(bottom // TILE_SIZE), 0)
        tile_top = min(int((top - 1) // TILE_SIZE), max(level_height - 1, 0))

        for tile_y in range(tile_bottom, tile_top + 1):
            for tile_x in range(tile_left, tile_right + 1):
                tile_slug = tile_lookup(tile_x, tile_y)
                if tile_slug == empty_slug:
                    continue

                tile_def = definition_lookup(tile_slug)
                if tile_def is None:
                    continue
                if tile_def.category != self._COLLECTABLE_CATEGORY:
                    continue

                yield (tile_x, tile_y)
