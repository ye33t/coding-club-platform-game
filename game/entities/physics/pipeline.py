"""Pipeline runner for entity physics processors."""

from __future__ import annotations

from typing import Iterable, List

from .base import EntityPhysicsContext, EntityProcessor


class EntityPipeline:
    """Sequenced runner that executes entity physics processors."""

    def __init__(self, processors: Iterable[EntityProcessor]):
        """Initialize the pipeline with the ordered processors."""
        self._processors: List[EntityProcessor] = list(processors)

    def process(self, context: EntityPhysicsContext) -> EntityPhysicsContext:
        """Run the context through each processor in order."""
        for processor in self._processors:
            context = processor.process(context)
        return context
