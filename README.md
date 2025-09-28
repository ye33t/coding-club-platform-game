# NES Platform Game - Architecture Study

A 2D platform game implementation demonstrating clean architecture principles and game programming patterns.

## Setup

```bash
# Install dependencies
poetry install

# Run the game
poetry run game

# Format and lint code
poetry run format
```

## Architecture

This project uses an **intent-based architecture** with strict separation of concerns:

1. **Input Processing**: `Mario.read_input()` → `MarioIntent`
2. **State Resolution**: `World.resolve_intent()` → `MarioState`
3. **State Application**: `Mario.apply_state()`
4. **Rendering**: `Mario.draw()`

The key principle: Mario expresses intent, World enforces physics, Mario accepts reality.

## Code Organization

```
game/
├── game.py          # Main game loop and event handling
├── mario.py         # Mario's state definition and rendering
├── world.py         # Physics engine and collision detection
├── display.py       # Display scaling and double buffering
├── sprites.py       # Sprite sheet management (singleton pattern)
├── sprite_sheet.py  # Individual sprite sheet loading
├── constants.py     # Game configuration values
└── sprite_definitions.py # Sprite coordinate mappings
```

## Core Concepts to Research

### Object-Oriented Programming
- **Classes and Instances**: `Mario` class vs `mario` instance
- **Encapsulation**: Mario's internal state is protected
- **Dataclasses**: `@dataclass` decorator for `MarioState` and `MarioIntent`

### Design Patterns
- **Singleton Pattern**: `SpriteManager._instance`
- **State Machine**: Mario's action transitions (idle → walking → running)
- **Entity-Component Pattern**: Separation of state from behavior

### Python Concepts
- **Type Annotations**: `def read_input(self, keys) -> MarioIntent`
- **Deep Copying**: Why `MarioState.clone()` uses `deepcopy`
- **Object References**: Why we need to clone state before modifying

## Key Design Decisions

### Coordinate System
- **Bottom-up coordinates**: y=0 at screen bottom, y increases upward
- Matches mathematical convention, not screen convention
- Research: Cartesian coordinates vs screen space

### Animation System
- **Frame-based timing**: Each frame = 1/60th second at 60 FPS
- Deterministic animation (same every time)
- Research: Frame-dependent vs delta-time animation

### State Management
- **Immutable updates**: Clone state, modify clone, replace old state
- Prevents accidental mutations
- Research: Functional programming, immutability benefits

## Study Order

1. **Start with `constants.py`**
   - Understand the coordinate system
   - See the NES resolution (256x224)
   - Note the tile-based design (8x8 pixels)

2. **Read `mario.py`**
   - Study the `MarioIntent` dataclass (user desires)
   - Study the `MarioState` dataclass (actual state)
   - Understand the separation between intent and state

3. **Examine `world.py`**
   - See how physics is calculated
   - Understand `resolve_intent()` transformation
   - Note collision detection logic

4. **Review `game.py`**
   - Understand the game loop: handle_events → update → draw
   - See the 60 FPS timing with `clock.tick(FPS)`
   - Note the display presentation pipeline

## Exercises

### Understanding the Code
1. **Trace a key press**: Follow arrow key from `handle_events()` to Mario moving
2. **Find the physics**: Locate where gravity, friction, and velocity are applied
3. **Understand animation**: How does Mario cycle through walking frames?

### Modifying Constants
1. Change `GRAVITY` from 400.0 to 200.0 - what happens?
2. Change `FRICTION` from 0.85 to 0.95 - how does movement feel?
3. Change `JUMP_VELOCITY` from 200.0 to 300.0 - what changes?

### Adding Features
1. **Double Jump**: Add a jump counter to `MarioState`, allow jumping in air once
2. **Sprint**: Make shift key increase `RUN_SPEED` to 160.0
3. **Crouch**: Add new state when down key pressed, reduce height

### Architecture Challenges
1. **Add platforms**: Create a `Platform` class, modify `World` collision
2. **Add enemies**: Design enemy state system similar to Mario
3. **Add scoring**: Where should score be stored? (Hint: not in Mario)

## Computer Science Topics

### Finite State Machines (FSM)
- Mario's actions form a state machine
- States: idle, walking, running, jumping, skidding
- Research: Moore machines vs Mealy machines

### Game Loop Patterns
- **Fixed Timestep**: 60 updates per second regardless of display
- **Input-Update-Render**: Classic game loop structure
- Research: Variable timestep, interpolation, accumulator pattern

### Coordinate Transformations
- Converting bottom-up to top-down for rendering
- Tile coordinates to pixel coordinates
- Research: Affine transformations, matrix operations

### Sprite Animation
- Frame sequences stored as arrays
- Animation state tracking (frame index, total frames)
- Research: Sprite atlases, texture packing

## Development Tools

### Poetry
- Dependency management and virtual environments
- Research: pip vs Poetry, virtual environments, reproducible builds

### Code Quality Tools
- **Black**: Opinionated code formatter (line length, quotes)
- **isort**: Import statement organization
- **flake8**: Style guide enforcement (PEP 8)
- **mypy**: Static type checking

Research: Static analysis, linting, type systems

## Mathematical Concepts

### Vector Mathematics
- Position (x, y)
- Velocity (vx, vy)
- Acceleration (gravity)
- Research: Vector addition, scalar multiplication

### Physics Simulation
- Euler integration: `position += velocity * dt`
- Gravity as constant acceleration
- Friction as velocity dampening
- Research: Numerical integration, physics engines

## Further Study

### Advanced Topics
- Quadtree collision detection
- Spatial hashing
- Camera systems and scrolling
- Particle systems
- State synchronization (for multiplayer)

### Books to Read
- "Game Programming Patterns" by Robert Nystrom
- "Real-Time Rendering" by Akenine-Möller
- "The Art of Computer Programming" by Donald Knuth

### Online Resources
- Research "Entity Component System (ECS)"
- Study "Fixed timestep game loops"
- Learn about "Separating axis theorem" for collision

## Code Standards

This project follows:
- PEP 8 style guide
- Type annotations for all function signatures
- Docstrings for all classes and public methods
- Single responsibility principle
- Explicit over implicit

## Understanding the Architecture

The architecture enforces these rules:
1. Mario doesn't know about physics (World's job)
2. World doesn't know about rendering (Mario's job)
3. State is never modified in place (always cloned)
4. Animation is deterministic (frame-based, not time-based)

This separation allows for:
- Easy testing (mock any component)
- Clear debugging (know where to look)
- Simple extensions (add without breaking)

Remember: Good architecture makes the code obvious, not clever.