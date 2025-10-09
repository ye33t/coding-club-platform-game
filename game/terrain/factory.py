"""Factory for creating terrain behaviors from configuration."""

from typing import Any, Dict, Optional

from .base import TerrainBehavior
from .bounce import BounceBehavior
from .flagpole import FlagpoleBehavior
from .item_box import ItemBoxBehavior
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
            return ItemBoxBehavior()
        else:
            raise BehaviorFactoryError(
                f"Unknown behavior type '{behavior_type}'. "
                f"Available types: bounce, none, warp, flagpole, item_box"
            )
