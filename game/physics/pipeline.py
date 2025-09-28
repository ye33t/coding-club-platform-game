"""Physics pipeline that orchestrates all physics processors."""

from typing import List, Optional

from .action import ActionProcessor
from .base import PhysicsContext, PhysicsProcessor
from .boundaries import BoundaryProcessor
from .ceiling_collision import CeilingCollisionProcessor
from .gravity import GravityProcessor
from .ground_collision import GroundCollisionProcessor
from .intent import IntentProcessor
from .left_wall_collision import LeftWallCollisionProcessor
from .movement import MovementProcessor
from .right_wall_collision import RightWallCollisionProcessor
from .velocity import VelocityProcessor


class PhysicsPipeline:
    """Orchestrates physics processors in a defined order.

    The pipeline processes physics in this order:
    1. Intent - Convert player input to target states
    2. Movement - Apply friction/deceleration
    3. Gravity - Apply gravity and handle jumping
    4. Velocity - Update position from velocity
    5. Boundaries - Enforce world boundaries
    6. LeftWallCollision - Detect and resolve left wall hits
    7. RightWallCollision - Detect and resolve right wall hits
    8. CeilingCollision - Detect and resolve ceiling hits
    9. GroundCollision - Detect and resolve ground/slopes
    10. Action - Determine action from final state

    This order ensures that:
    - Input is processed first
    - Forces are applied (gravity, friction)
    - Position is updated
    - Collisions are resolved separately
    - Final action is determined
    """

    def __init__(self):
        """Initialize the pipeline with default processors."""
        self.processors: List[PhysicsProcessor] = [
            IntentProcessor(),
            MovementProcessor(),
            GravityProcessor(),
            VelocityProcessor(),
            BoundaryProcessor(),
            LeftWallCollisionProcessor(),
            RightWallCollisionProcessor(),
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
            The processed context
        """
        for processor in self.processors:
            if processor.is_enabled():
                if self.debug:
                    processor_name = processor.__class__.__name__
                    print(f"Processing: {processor_name}")
                    self._debug_state(context.state, f"Before {processor_name}")

                context = processor.process(context)

                if self.debug:
                    name = processor.__class__.__name__
                    self._debug_state(context.state, f"After {name}")

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

    def _debug_state(self, state, label: str) -> None:
        """Debug helper to print state."""
        print(
            f"  {label}: pos=({state.x:.1f}, {state.y:.1f}), "
            f"vel=({state.vx:.1f}, {state.vy:.1f}), "
            f"on_ground={state.on_ground}, action={state.action}"
        )
