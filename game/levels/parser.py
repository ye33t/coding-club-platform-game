"""Two-pass level parser for converting ASCII layouts to tile grids."""

from typing import List, Set, Tuple

from ..constants import TILES_HORIZONTAL, TILES_VERTICAL
from ..tile_definitions import empty_tile_slug, require_tile
from .converters import CONVERTERS
from .types import Compound, ParserContext


class ParseError(Exception):
    """Exception raised when parsing fails."""

    pass


class LevelParser:
    """Two-pass parser for level layouts."""

    def __init__(self):
        """Initialize the parser with tile mappings."""
        # Simple 1:1 character to tile mappings
        self.simple_tiles = {
            "#": require_tile("ground"),
            "=": require_tile("brick_top"),
            "@": require_tile("block"),
            ".": empty_tile_slug(),
        }

    def parse_screen(self, layout: str, screen_index: int = 0) -> List[List[str]]:
        """Parse a screen layout into a tile slug grid.

        The layout must be at least 16 columns wide and exactly 14 rows tall.

        Args:
            layout: ASCII art layout string
            screen_index: Index of the screen being parsed

        Returns:
            2D list of tile slugs (14 rows x N columns, where N >= 16)

        Raises:
            ParseError: If parsing fails
        """
        # Split and reverse lines (bottom-up coordinates)
        lines = layout.strip().split("\n")
        lines.reverse()

        # Validate dimensions
        if len(lines) != TILES_VERTICAL:
            raise ParseError(
                f"Layout must have {TILES_VERTICAL} rows, got {len(lines)}"
            )

        # Check that all rows have the same length
        if not lines:
            raise ParseError("Layout is empty")

        width = len(lines[0])
        if width < TILES_HORIZONTAL:
            raise ParseError(
                f"Layout width must be at least {TILES_HORIZONTAL}, got {width}"
            )

        for i, line in enumerate(lines):
            if len(line) != width:
                raise ParseError(
                    f"Row {i} has {len(line)} characters, expected {width} "
                    "(all rows must be the same length)"
                )

        # Create context
        context = ParserContext(
            layout=lines,
            width=width,
            height=TILES_VERTICAL,
            screen_index=screen_index,
        )

        # Pass 1: Lexer - find compounds (contiguous regions)
        compounds = self._lexer_pass(context)

        # Pass 2: Parser - convert compounds to tiles
        tiles = self._parser_pass(compounds, context)

        # Check for errors
        if context.errors:
            raise ParseError("\n".join(context.errors))

        return tiles

    def _lexer_pass(self, context: ParserContext) -> List[Compound]:
        """Lexer pass: Find all connected regions of the same character.

        Args:
            context: Parser context

        Returns:
            List of compounds (contiguous regions of the same character)
        """
        compounds = []
        visited = set()

        for y in range(context.height):
            for x in range(context.width):
                if (x, y) in visited:
                    continue

                char = context.get_char(x, y)

                # Skip if out of bounds
                if char is None:
                    continue

                # Simple tiles - mark as visited but don't create compounds
                if char in self.simple_tiles:
                    visited.add((x, y))
                    continue

                # For any compound character, flood fill to find connected region
                component = self._flood_fill(x, y, char, context, visited)
                if component:
                    # Convert positions set to mask
                    xs = {x for x, y in component}
                    ys = {y for x, y in component}
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)

                    # Create 2D mask
                    width = max_x - min_x + 1
                    height = max_y - min_y + 1
                    mask = [[False for _ in range(width)] for _ in range(height)]

                    # Fill mask based on positions
                    for px, py in component:
                        mask[py - min_y][px - min_x] = True

                    compounds.append(
                        Compound(
                            character=char,
                            mask=mask,
                            origin_x=min_x,
                            origin_y=min_y,
                        )
                    )

        return compounds

    def _flood_fill(
        self,
        start_x: int,
        start_y: int,
        target_char: str,
        context: ParserContext,
        visited: Set[Tuple[int, int]],
    ) -> Set[Tuple[int, int]]:
        """Flood fill to find connected region of the same character.

        Args:
            start_x: Starting X position
            start_y: Starting Y position
            target_char: The character to match
            context: Parser context
            visited: Set of already visited positions

        Returns:
            Set of positions forming the connected component
        """
        component = set()
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue

            char = context.get_char(x, y)
            if char != target_char:
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

    def _parser_pass(
        self, compounds: List[Compound], context: ParserContext
    ) -> List[List[str]]:
        """Parser pass: Convert compounds and simple tiles to final tile grid.

        Args:
            compounds: List of compounds to convert
            context: Parser context

        Returns:
            2D list of tile slugs
        """
        # Initialize with empty tiles
        empty = empty_tile_slug()
        tiles = [[empty for _ in range(context.width)] for _ in range(context.height)]

        # Track which positions have been processed
        processed = set()

        # Convert compounds using registered converters
        for compound in compounds:
            converter = CONVERTERS.get(compound.character)
            if converter:
                tile_placement = converter(compound, context)
                if tile_placement:
                    for (x, y), tile_slug in tile_placement.items():
                        tiles[y][x] = tile_slug
                        processed.add((x, y))
            else:
                # Unknown compound character - add to context errors
                context.add_error(
                    f"No converter found for compound '{compound.character}' "
                    f"at ({compound.origin_x}, {compound.origin_y})"
                )

        # Convert simple tiles
        for y in range(context.height):
            for x in range(context.width):
                if (x, y) in processed:
                    continue

                char = context.get_char(x, y)
                if char in self.simple_tiles:
                    tiles[y][x] = self.simple_tiles[char]

        return tiles

    def parse_zones(self, zones: str, width: int, height: int) -> List[List[str]]:
        """Parse a zones grid into a 2D character array.

        Args:
            zones: ASCII zones string
            width: Expected width in tiles
            height: Expected height in tiles

        Returns:
            2D list of zone characters (height rows x width columns)

        Raises:
            ParseError: If parsing fails or dimensions don't match
        """
        # Split and reverse lines (bottom-up coordinates)
        lines = zones.strip().split("\n")
        lines.reverse()

        # Validate dimensions
        if len(lines) != height:
            raise ParseError(
                f"Zones grid must have {height} rows to match layout, got {len(lines)}"
            )

        if not lines:
            raise ParseError("Zones grid is empty")

        for i, line in enumerate(lines):
            if len(line) != width:
                raise ParseError(
                    f"Zones row {i} has {len(line)} characters, expected {width} "
                    "to match layout width"
                )

        # Convert to 2D array of characters
        return [[char for char in line] for line in lines]
