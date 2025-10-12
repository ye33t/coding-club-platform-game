# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development

```bash
# Run the game
poetry run game

# Format and lint code (runs isort, black, flake8, mypy)
poetry run format

# Run tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/physics/test_gravity_processor.py

# Run test matching pattern
poetry run pytest -k "test_gravity"

# Run tests with coverage
poetry run pytest --cov=game --cov-report=term-missing
```

## Architecture

This is an NES-style platform game using an **intent-based physics pipeline architecture**. The key architectural principle: **Mario expresses intent, World enforces physics through pipeline, Mario accepts reality**.

### Core Flow

1. **Input** → `Mario.get_intent()` → `MarioIntent` (what player wants)
2. **Physics** → `PhysicsPipeline.process()` mutates live Mario/camera state
3. **Post-Physics** → `Mario.post_physics_update()` adjusts animation metadata
4. **Rendering** → `Mario.draw()` → Visual representation

### Physics Pipeline

The game uses a modular physics pipeline (`game/physics/pipeline.py`) with processors executed in strict order:

1. **IntentProcessor** - Converts player input to physics targets
2. **DeathPhysicsProcessor** - Handles death animation physics (early to override others)
3. **MovementProcessor** - Applies friction and deceleration
4. **GravityProcessor** - Applies gravity and jump physics
5. **VelocityProcessor** - Updates position from velocity
6. **DeathTriggerProcessor** - Checks if Mario fell below screen
7. **ResetProcessor** - Checks if death animation is complete
8. **BoundaryProcessor** - Enforces world boundaries
9. **LeftWallCollisionProcessor** - Resolves left wall collisions
10. **RightWallCollisionProcessor** - Resolves right wall collisions
11. **CeilingCollisionProcessor** - Resolves ceiling collisions
12. **GroundCollisionProcessor** - Resolves ground/slope collisions
13. **ActionProcessor** - Determines final action from state

Each processor:

- Implements `PhysicsProcessor` interface
- Takes `PhysicsContext`, returns modified `PhysicsContext`
- Is stateless and independent
- Can be enabled/disabled

### Key Design Patterns

- **Pipeline Pattern**: Physics processors chained together
- **Live State Mutation**: Physics processors operate on Mario and camera directly, with short-circuit processors running before state changes
- **Separation of Concerns**: Mario handles rendering, World handles physics, Level handles terrain
- **Singleton Pattern**: `SpriteManager` for sprite sheet management
- **State Machine**: Mario actions (idle, walking, running, jumping, skidding)

### Coordinate System

- **Bottom-up coordinates**: y=0 at screen bottom, y increases upward
- NES resolution: 256x224 pixels
- Tile-based: 8x8 pixel tiles
- Camera follows Mario with configurable dead zones

## Testing

Tests are located in `tests/` directory with pytest fixtures in `conftest.py`. Key test patterns:

- Unit tests for individual physics processors
- Integration tests for physics pipeline
- Reuse existing builders/fixtures for intents and entities where available
- Test both normal and edge cases (death, boundaries, collisions)

## Code Standards

- **Python 3.13** with type annotations
- **Black** formatter (88 char lines)
- **isort** for imports
- **flake8** for linting
- **mypy** for type checking
- Follow PEP 8
- Dataclasses for state objects
- No inline comments unless complex algorithm
