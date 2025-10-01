"""Two-pass level parser for converting ASCII layouts to tile grids."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ..tile_definitions import (
    TILE_BLOCK,
    TILE_BRICK_TOP,
    TILE_EMPTY,
    TILE_GROUND,
    TILE_PIPE_LEFT,
    TILE_PIPE_RIGHT,
    TILE_PIPE_TOP_LEFT,
    TILE_PIPE_TOP_RIGHT,
)


@dataclass
class ParserContext:
    """Context carried through parsing operations."""

    layout: List[str]  # The full screen layout (bottom-up)
    width: int
    height: int
    screen_index: int
    errors: List[str] = field(default_factory=list)

    def get_char(self, x: int, y: int) -> Optional[str]:
        """Safe character access with bounds checking."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.layout[y][x]
        return None

    def add_error(self, message: str) -> None:
        """Add an error message to the context."""
        self.errors.append(f"Screen {self.screen_index}: {message}")


@dataclass
class Compound:
    """Represents a connected group of characters forming a pattern."""

    pattern_type: str  # Type of pattern ('pipe', etc.)
    positions: Set[Tuple[int, int]]  # All positions in this compound
    bounds: Tuple[int, int, int, int]  # min_x, min_y, max_x, max_y


class ParseError(Exception):
    """Exception raised when parsing fails."""

    pass


class LevelParser:
    """Two-pass parser for level layouts."""

    def __init__(self):
        """Initialize the parser with tile mappings."""
        # Simple 1:1 character to tile mappings
        self.simple_tiles = {
            "#": TILE_GROUND,
            "=": TILE_BRICK_TOP,
            "@": TILE_BLOCK,
            ".": TILE_EMPTY,
        }

    def parse_screen(self, layout: str, screen_index: int = 0) -> List[List[int]]:
        """Parse a screen layout into a tile grid.

        Args:
            layout: ASCII art layout string
            screen_index: Index of the screen being parsed

        Returns:
            2D list of tile IDs (14 rows x 16 columns)

        Raises:
            ParseError: If parsing fails
        """
        # Split and reverse lines (bottom-up coordinates)
        lines = layout.strip().split("\n")
        lines.reverse()

        # Validate dimensions
        if len(lines) != 14:
            raise ParseError(f"Screen must have 14 rows, got {len(lines)}")
        for i, line in enumerate(lines):
            if len(line) != 16:
                raise ParseError(f"Row {i} must have 16 characters, got {len(line)}")

        # Create context
        context = ParserContext(
            layout=lines,
            width=16,
            height=14,
            screen_index=screen_index,
        )

        # Pass 1: Find compounds
        compounds = self._find_compounds(context)

        # Pass 2: Convert to tiles
        tiles = self._convert_to_tiles(compounds, context)

        # Check for errors
        if context.errors:
            raise ParseError("\n".join(context.errors))

        return tiles

    def _find_compounds(self, context: ParserContext) -> List[Compound]:
        """Pass 1: Find all connected components that form patterns.

        Args:
            context: Parser context

        Returns:
            List of compounds found
        """
        compounds = []
        visited = set()

        for y in range(context.height):
            for x in range(context.width):
                if (x, y) in visited:
                    continue

                char = context.get_char(x, y)

                # Simple tiles or empty - skip
                if char in self.simple_tiles:
                    visited.add((x, y))
                    continue

                # Pipe pattern
                if char == "|":
                    # Find all connected pipe characters
                    component = self._flood_fill_pipes(x, y, context, visited)
                    if component:
                        # Validate it forms a valid pipe
                        if self._validate_pipe(component, context):
                            bounds = self._get_bounds(component)
                            compounds.append(
                                Compound(
                                    pattern_type="pipe",
                                    positions=component,
                                    bounds=bounds,
                                )
                            )

        return compounds

    def _flood_fill_pipes(
        self, start_x: int, start_y: int, context: ParserContext, visited: Set[Tuple[int, int]]
    ) -> Set[Tuple[int, int]]:
        """Flood fill to find connected pipe characters.

        Args:
            start_x: Starting X position
            start_y: Starting Y position
            context: Parser context
            visited: Set of already visited positions

        Returns:
            Set of positions forming the pipe component
        """
        component = set()
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue

            char = context.get_char(x, y)
            if char != "|":
                continue

            visited.add((x, y))
            component.add((x, y))

            # Check 4-connected neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < context.width and 0 <= ny < context.height:
                    if (nx, ny) not in visited:
                        stack.append((nx, ny))

        return component

    def _validate_pipe(self, component: Set[Tuple[int, int]], context: ParserContext) -> bool:
        """Validate that a component forms a valid pipe.

        Pipes must be exactly 2 characters wide and vertically connected.

        Args:
            component: Set of positions in the component
            context: Parser context

        Returns:
            True if valid pipe, False otherwise
        """
        if not component:
            return False

        # Get bounds
        xs = {x for x, y in component}
        ys = {y for x, y in component}

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Check if it's 2 wide
        if max_x - min_x != 1:
            context.add_error(f"Pipe at ({min_x}, {min_y}) must be exactly 2 characters wide")
            return False

        # Check that it forms a proper rectangle (all positions filled)
        expected_positions = set()
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                expected_positions.add((x, y))

        if component != expected_positions:
            context.add_error(f"Pipe at ({min_x}, {min_y}) has gaps - must be solid rectangle")
            return False

        return True

    def _get_bounds(self, component: Set[Tuple[int, int]]) -> Tuple[int, int, int, int]:
        """Get the bounding box of a component.

        Args:
            component: Set of positions

        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        xs = {x for x, y in component}
        ys = {y for x, y in component}
        return (min(xs), min(ys), max(xs), max(ys))

    def _convert_to_tiles(
        self, compounds: List[Compound], context: ParserContext
    ) -> List[List[int]]:
        """Pass 2: Convert compounds and simple tiles to final tile grid.

        Args:
            compounds: List of compounds to convert
            context: Parser context

        Returns:
            2D list of tile IDs
        """
        # Initialize with empty tiles
        tiles = [[TILE_EMPTY for _ in range(16)] for _ in range(14)]

        # Track which positions have been processed
        processed = set()

        # Convert compounds first
        for compound in compounds:
            if compound.pattern_type == "pipe":
                pipe_tiles = self._convert_pipe(compound, context)
                for (x, y), tile_id in pipe_tiles.items():
                    tiles[y][x] = tile_id
                    processed.add((x, y))

        # Convert simple tiles
        for y in range(context.height):
            for x in range(context.width):
                if (x, y) in processed:
                    continue

                char = context.get_char(x, y)
                if char in self.simple_tiles:
                    tiles[y][x] = self.simple_tiles[char]

        return tiles

    def _convert_pipe(
        self, compound: Compound, context: ParserContext
    ) -> Dict[Tuple[int, int], int]:
        """Convert a pipe compound to tile placements.

        Args:
            compound: Pipe compound to convert
            context: Parser context

        Returns:
            Dictionary mapping positions to tile IDs
        """
        tiles = {}
        min_x, min_y, max_x, max_y = compound.bounds

        for y in range(min_y, max_y + 1):
            # Check if this is the top of the pipe
            is_top = y == min_y

            if is_top:
                # Top tiles
                tiles[(min_x, y)] = TILE_PIPE_TOP_LEFT
                tiles[(min_x + 1, y)] = TILE_PIPE_TOP_RIGHT
            else:
                # Body tiles
                tiles[(min_x, y)] = TILE_PIPE_LEFT
                tiles[(min_x + 1, y)] = TILE_PIPE_RIGHT

        return tiles