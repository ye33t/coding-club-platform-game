"""Physics pipeline that orchestrates all physics processors."""

from typing import List, Optional

from .action import ActionProcessor
from .base import PhysicsContext, PhysicsProcessor
from .boundaries import BoundaryProcessor
from .ceiling_collision import CeilingCollisionProcessor
from .death_event import DeathEventProcessor
from .gravity import GravityProcessor
from .ground_collision import GroundCollisionProcessor
from .intent import IntentProcessor
from .movement import MovementProcessor
from .velocity import VelocityProcessor
from .wall_collision import Direction, WallCollisionProcessor
from .warp_event import WarpEventProcessor


class PhysicsPipeline:
    """Orchestrates physics processors in a defined order.

    The pipeline processes physics in this order:
    1. Intent - Convert player input to target states
    2. DeathEvent - Check if Mario fell below screen (short-circuits)
    3. WarpEvent - Check if Mario is warping (short-circuits)
    4. Movement - Apply friction/deceleration
    5. Gravity - Apply gravity and handle jumping
    6. Velocity - Update position from velocity
    7. Boundaries - Enforce world boundaries
    8. WallCollision (LEFT) - Detect and resolve left wall hits
    9. WallCollision (RIGHT) - Detect and resolve right wall hits
    10. CeilingCollision - Detect and resolve ceiling hits
    11. GroundCollision - Detect and resolve ground/slopes
    12. Action - Determine action from final state

    This order ensures that:
    - Input is processed first
    - Game events are detected early and short-circuit the pipeline
    - Forces are applied (gravity, friction)
    - Position is updated
    - Collisions are resolved separately
    - Final action is determined
    """

    def __init__(self):
        """Initialize the pipeline with default processors."""
        self.processors: List[PhysicsProcessor] = [
            IntentProcessor(),
            DeathEventProcessor(),
            WarpEventProcessor(),
            MovementProcessor(),
            GravityProcessor(),
            VelocityProcessor(),
            BoundaryProcessor(),
            WallCollisionProcessor(Direction.LEFT),
            WallCollisionProcessor(Direction.RIGHT),
            CeilingCollisionProcessor(),
            GroundCollisionProcessor(),
            ActionProcessor(),
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
                    self._debug_state(context.mario_state, f"Before {processor_name}")

                context = processor.process(context)

                if self.debug:
                    name = processor.__class__.__name__
                    self._debug_state(context.mario_state, f"After {name}")

                # Short-circuit if an event was raised
                if context.event is not None:
                    if self.debug:
                        print(f"Event raised: {context.event.__class__.__name__}")
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

    def _debug_state(self, mario_state, label: str) -> None:
        """Debug helper to print state."""
        print(
            f"  {label}: pos=({mario_state.x:.1f}, {mario_state.y:.1f}), "
            f"vel=({mario_state.vx:.1f}, {mario_state.vy:.1f}), "
            f"on_ground={mario_state.on_ground}, action={mario_state.action}"
        )
