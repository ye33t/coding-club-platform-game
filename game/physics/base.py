"""Base classes for the physics pipeline system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Set

from ..mario import MarioIntent

if TYPE_CHECKING:
    from ..camera import Camera
    from ..entities import Entity
    from ..level import Level
    from ..mario import Mario
    from .events import PhysicsEvent


@dataclass
class PhysicsContext:
    """Carries data through the physics pipeline.

    This context object is passed through each processor in the pipeline,
    allowing processors to access and modify the state and supporting data.
    """

    mario: "Mario"  # Live Mario instance (state mutated in place)
    camera: "Camera"  # Live camera instance mutated in place
    mario_intent: MarioIntent  # What the player wants Mario to do
    level: "Level"  # Level data for collision detection
    dt: float  # Delta time for this frame
    event: Optional["PhysicsEvent"] = None  # Event that triggers state transition
    entities: List["Entity"] = field(default_factory=list)  # Active game entities
    entities_to_remove: Set["Entity"] = field(
        default_factory=set
    )  # Entities flagged for removal during processing

class PhysicsProcessor(ABC):
    """Abstract base class for physics processors.

    Each processor handles one aspect of physics simulation.
    Processors are designed to be:
    - Single responsibility (do one thing well)
    - Composable (can be combined in different orders)
    - Testable (can be tested in isolation)
    - Extensible (easy to add new processors)
    """

    @abstractmethod
    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process the physics context.

        Args:
            context: The current physics context

        Returns:
            The modified context (can be the same object)
        """
        pass

    def is_enabled(self) -> bool:
        """Check if this processor should be active.

        Can be overridden for conditional processing.

        Returns:
            True if processor should run, False to skip
        """
        return True
