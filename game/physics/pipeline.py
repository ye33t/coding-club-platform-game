"""Physics pipeline that orchestrates all physics processors."""

from typing import TYPE_CHECKING, List, Optional

from .action import ActionProcessor
from .base import PhysicsContext, PhysicsProcessor
from .boundaries import BoundaryProcessor
from .ceiling_collision import CeilingCollisionProcessor
from .death_event import DeathEventProcessor
from .end_level_event import EndLevelEventProcessor
from .entity_collision import EntityCollisionProcessor
from .flagpole_clamp import FlagpoleClampProcessor
from .gravity import GravityProcessor
from .ground_collision import GroundCollisionProcessor
from .intent import IntentProcessor
from .movement import MovementProcessor
from .power_up import MarioTransitionProcessor
from .terrain_behaviors import TerrainBehaviorProcessor
from .velocity import VelocityProcessor
from .wall_collision import Direction, WallCollisionProcessor
from .warp_event import WarpEventProcessor

if TYPE_CHECKING:
    from ..mario import Mario


class PhysicsPipeline:
    """Orchestrates physics processors in a defined order."""

    def __init__(self) -> None:
        """Initialize the pipeline with default processors."""
        self.processors: List[PhysicsProcessor] = [
            EndLevelEventProcessor(),
            WarpEventProcessor(),
            DeathEventProcessor(),
            EntityCollisionProcessor(),
            IntentProcessor(),
            MovementProcessor(),
            GravityProcessor(),
            VelocityProcessor(),
            BoundaryProcessor(),
            WallCollisionProcessor(Direction.LEFT),
            WallCollisionProcessor(Direction.RIGHT),
            CeilingCollisionProcessor(),
            GroundCollisionProcessor(),
            FlagpoleClampProcessor(),
            TerrainBehaviorProcessor(),
            ActionProcessor(),
            MarioTransitionProcessor(),
        ]

        # Optional: Enable/disable debugging
        self.debug = False

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process the context through all processors.

        Args:
            context: The initial physics context

        Returns:
            The processed context (may contain an event that short-circuits)
        """
        for processor in self.processors:
            if processor.is_enabled():
                if self.debug:
                    processor_name = processor.__class__.__name__
                    print(f"Processing: {processor_name}")
                    self._debug_state(context.mario, f"Before {processor_name}")

                context = processor.process(context)

                if self.debug:
                    name = processor.__class__.__name__
                    self._debug_state(context.mario, f"After {name}")

                # Short-circuit if an event was raised
                if context.has_short_circuit_event():
                    if self.debug:
                        latest = next(
                            evt for evt in reversed(context.events) if evt.short_circuit
                        )
                        print(f"Event raised: {latest.__class__.__name__}")
                    return context

        return context

    def add_processor(
        self, processor: PhysicsProcessor, position: Optional[int] = None
    ) -> None:
        """Add a processor to the pipeline.

        Args:
            processor: The processor to add
            position: Optional position in pipeline (None = end)
        """
        if position is None:
            self.processors.append(processor)
        else:
            self.processors.insert(position, processor)

    def remove_processor(self, processor_type: type) -> None:
        """Remove all processors of a given type.

        Args:
            processor_type: The type of processor to remove
        """
        self.processors = [
            p for p in self.processors if not isinstance(p, processor_type)
        ]

    def _debug_state(self, mario: "Mario", label: str) -> None:
        """Debug helper to print state."""
        print(
            f"  {label}: pos=({mario.x:.1f}, {mario.y:.1f}), "
            f"vel=({mario.vx:.1f}, {mario.vy:.1f}), "
            f"on_ground={mario.on_ground}, action={mario.action}"
        )
