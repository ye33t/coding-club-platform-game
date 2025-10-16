"""Factory for creating terrain behaviors from configuration."""

from typing import Any, Dict, Optional

from .base import TerrainBehavior
from .bounce import BounceBehavior
from .castle_exit import CastleExitBehavior
from .flagpole import FlagpoleBehavior
from .item_box import ItemBoxBehavior, ItemBoxSpawnType
from .none import NoneBehavior
from .warp import WarpBehavior


class BehaviorFactoryError(Exception):
    """Exception raised when behavior creation fails."""

    pass


class BehaviorFactory:
    """Factory for creating terrain behavior instances from configuration."""

    def create(
        self, behavior_type: str, params: Optional[Dict[str, Any]] = None
    ) -> TerrainBehavior:
        """Create a behavior instance from a type string with optional parameters.

        Args:
            behavior_type: The type of behavior to create (e.g., "bounce", "warp")
            params: Optional dictionary of parameters for the behavior

        Returns:
            An instance of the requested behavior

        Raises:
            BehaviorFactoryError: If behavior type is unknown or parameters are invalid
        """
        if behavior_type == "bounce":
            one_shot = params.get("one_shot", False) if params else False
            return BounceBehavior(one_shot=one_shot)
        elif behavior_type == "none":
            return NoneBehavior()
        elif behavior_type == "warp":
            if not params:
                raise BehaviorFactoryError("Warp behavior requires parameters")
            if "to_screen" not in params:
                raise BehaviorFactoryError(
                    "Warp behavior missing required parameter: to_screen"
                )
            if "to_zone" not in params:
                raise BehaviorFactoryError(
                    "Warp behavior missing required parameter: to_zone"
                )
            return WarpBehavior(params["to_screen"], params["to_zone"])
        elif behavior_type == "flagpole":
            return FlagpoleBehavior()
        elif behavior_type == "item_box":
            spawn_param = params.get("spawn") if params else None
            if spawn_param is None:
                spawn_type = ItemBoxSpawnType.COIN
            elif isinstance(spawn_param, str):
                try:
                    spawn_type = ItemBoxSpawnType.from_string(spawn_param)
                except ValueError as exc:
                    raise BehaviorFactoryError(str(exc)) from exc
            else:
                raise BehaviorFactoryError(
                    "Item box spawn parameter must be a string if provided."
                )

            spawn_count_param = params.get("spawns") if params else None
            if spawn_count_param is None:
                spawn_count = 1
            elif isinstance(spawn_count_param, int):
                if spawn_count_param < 1:
                    raise BehaviorFactoryError(
                        "Item box spawns parameter must be at least 1."
                    )
                spawn_count = spawn_count_param
            else:
                raise BehaviorFactoryError(
                    "Item box spawns parameter must be an integer if provided."
                )
            return ItemBoxBehavior(spawn_type=spawn_type, spawn_count=spawn_count)
        elif behavior_type == "castle_exit":
            if not params or "role" not in params:
                raise BehaviorFactoryError(
                    "castle_exit behavior requires a 'role' parameter."
                )

            role = params["role"]
            if not isinstance(role, str):
                raise BehaviorFactoryError(
                    "castle_exit role parameter must be a string."
                )

            offset_x = params.get("offset_x", 0.0)
            offset_y = params.get("offset_y", 0.0)
            start_offset_y = params.get("start_offset_y")

            try:
                offset_x = float(offset_x)
                offset_y = float(offset_y)
                if start_offset_y is not None:
                    start_offset_y = float(start_offset_y)
            except (TypeError, ValueError) as exc:
                raise BehaviorFactoryError(
                    "castle_exit offsets must be numbers if provided."
                ) from exc

            return CastleExitBehavior(
                role=role,
                offset_x=offset_x,
                offset_y=offset_y,
                start_offset_y=start_offset_y,
            )
        else:
            raise BehaviorFactoryError(
                f"Unknown behavior type '{behavior_type}'. "
                "Available types: bounce, none, warp, flagpole, item_box, castle_exit"
            )
