"""Base classes for the physics pipeline system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..camera import Camera
from ..level import Level
from ..mario import MarioIntent, MarioState


@dataclass
class PhysicsContext:
    """Carries data through the physics pipeline.

    This context object is passed through each processor in the pipeline,
    allowing processors to access and modify the state and access level data.
    """

    mario: MarioState  # The current/evolving state of Mario
    mario_intent: MarioIntent  # What the player wants Mario to do
    level: Level  # Level data for collision detection
    camera: Camera  # Camera for boundary checks
    dt: float  # Delta time for this frame

    # Future extensibility - these will be added as needed:
    # enemies: List[Enemy] = field(default_factory=list)
    # items: List[Item] = field(default_factory=list)
    # effects: List[Effect] = field(default_factory=list)


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
