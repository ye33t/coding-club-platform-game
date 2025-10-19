"""Item box behavior that spawns configured rewards, tracks spawns, and bounces."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..constants import TILE_SIZE
from ..effects.coin import CoinEffect
from ..entities.mushroom import MushroomEntity
from ..gameplay import HUD_COIN_INCREMENT
from ..physics.events import (
    CollectCoinEvent,
    SpawnEffectEvent,
    SpawnEntityEvent,
    TerrainTileChangeEvent,
)
from .base import BehaviorContext, TerrainBehavior, TileEvent
from .bounce import BounceBehavior


class ItemBoxSpawnType(Enum):
    """Available rewards that an item box can produce."""

    COIN = "coin"
    MUSHROOM = "mushroom"

    @classmethod
    def from_string(cls, raw_value: str) -> "ItemBoxSpawnType":
        """Parse a spawn type from configuration input."""
        normalized = raw_value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValueError(f"Unknown item box spawn type '{raw_value}'") from exc


@dataclass(slots=True)
class ItemBoxBehavior(TerrainBehavior):
    """Spawns rewards until depleted, then turns into a used item box."""

    spawn_type: ItemBoxSpawnType = ItemBoxSpawnType.COIN
    spawn_count: int = 1
    bounce_behavior: BounceBehavior = field(default_factory=BounceBehavior)

    def __post_init__(self) -> None:
        if self.spawn_count < 1:
            raise ValueError("Item box spawn_count must be at least 1.")

    def process(self, context: BehaviorContext) -> None:
        state = context.state
        remaining_spawns = state.data.get("remaining_spawns")

        if remaining_spawns is None:
            remaining_spawns = self.spawn_count
            state.data["remaining_spawns"] = remaining_spawns

        if context.event == TileEvent.HIT_FROM_BELOW and remaining_spawns > 0:

            remaining_spawns -= 1
            state.data["remaining_spawns"] = remaining_spawns

            if self.spawn_type is ItemBoxSpawnType.COIN:
                coin_x = context.tile_x * TILE_SIZE
                coin_y = (context.tile_y + 1) * TILE_SIZE
                context.physics.add_event(
                    SpawnEffectEvent(
                        effect=CoinEffect(
                            world_x=coin_x,
                            world_y=coin_y,
                        )
                    )
                )
                context.physics.add_event(CollectCoinEvent(amount=HUD_COIN_INCREMENT))
            elif self.spawn_type is ItemBoxSpawnType.MUSHROOM:
                mushroom_x = context.tile_x * TILE_SIZE
                mushroom_y = context.tile_y * TILE_SIZE + (TILE_SIZE // 4)
                context.physics.add_event(
                    SpawnEntityEvent(
                        entity=MushroomEntity(
                            world_x=mushroom_x,
                            world_y=mushroom_y,
                            screen=context.screen,
                            facing_right=True,
                        )
                    )
                )

            if remaining_spawns == 0:
                context.physics.add_event(
                    TerrainTileChangeEvent(
                        screen=context.screen,
                        x=context.tile_x,
                        y=context.tile_y,
                        slug="item_box_used",
                        behavior_type="bounce",
                        behavior_params={"one_shot": True},
                    )
                )

        # Update bounce animation each frame to reuse shared behavior logic.
        self.bounce_behavior.process(context)
