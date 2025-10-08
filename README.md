# NES Platform Game - Learn Game Programming

A 2D platform game where you'll learn how video games really work.

## Setup

```bash
# Install dependencies
poetry install

# Run the game
poetry run game

# Format and lint code
poetry run format

# Run existing smoke tests (no new tests should be added right now)
poetry run pytest
```

## Testing

We keep the legacy smoke test around, but we're **not writing new automated tests** at the moment. Focus on manual playtesting when making changes; running `poetry run pytest` is still useful to ensure the existing check passes.

## Architecture (How the Game Works Inside)

This game uses a **physics pipeline** - like an assembly line for game physics!

### The Game Flow (Every Frame)

1. **Read Input**: Check what keys the player pressed
2. **Mario's Intent**: Mario says "I want to jump!" or "I want to run right!"
3. **Physics Pipeline**: A bunch of processors that work in order:
   - Apply gravity (Mario falls)
   - Apply friction (Mario slows down)
   - Check collisions (Mario can't go through walls)
   - And more!
4. **Update Mario**: Mario accepts what physics says happened
5. **Draw Screen**: Show Mario in his new position

The cool part: Mario doesn't calculate physics himself - the pipeline does it for him!

## Code Organization

```
game/
├── game.py          # Main game loop and event handling
├── mario.py         # Mario's state definition and rendering
├── world.py         # Orchestrates the physics pipeline
├── physics/         # Physics pipeline processors
│   ├── pipeline.py  # Main pipeline that runs all processors
│   ├── base.py      # Base classes for all processors
│   ├── intent.py    # Converts input to physics targets
│   ├── movement.py  # Applies friction and deceleration
│   ├── gravity.py   # Applies gravity and jumping
│   ├── velocity.py  # Updates position from velocity
│   └── ...          # Various collision processors
├── level.py         # Level layout and collision data
├── camera.py        # Camera following Mario
├── display.py       # Display scaling and double buffering
├── sprites.py       # Sprite sheet management (singleton pattern)
├── content/         # Asset loaders, sprite sheet helpers, and tile metadata
├── constants.py     # Game configuration values
└── assets/          # Art, level YAML, and runtime config data
```

## Programming Concepts You'll Learn

### Object-Oriented Programming (OOP)

- **Classes**: Think of a class as a blueprint (like `Mario` class)
- **Instances**: The actual object made from the blueprint (`mario` variable)
- **Encapsulation**: Keeping Mario's data safe from accidental changes

### Design Patterns (Smart Ways to Organize Code)

- **Singleton**: Only one sprite manager exists (like having one TV remote)
- **State Machine**: Mario's actions flow logically (can't run while idle)
- **Pipeline**: Physics processors work like an assembly line

### Python Skills

- **Type Hints**: Tells us what kind of data functions expect
- **Cloning Objects**: Making a copy so we don't mess up the original
- **Dataclasses**: Easy way to create classes that hold data

## How This Game Works

### The Coordinate System

- **Y goes UP** (like in math class!): Higher y = higher on screen
- Most games have y going down, but we chose the math way
- Makes physics calculations easier to understand

### Animation (Making Mario Move Smoothly)

- Game runs at 60 FPS (frames per second)
- Each frame shows a different Mario picture
- Your eye blends them together into smooth motion

### Safe State Changes

- We always copy Mario's state before changing it
- Like making a rough draft before the final version
- Prevents weird bugs from accidental changes

## Study Order

1. **Start with `constants.py`**
   - Understand the coordinate system
   - See the NES resolution (256x224)
   - Note the tile-based design (8x8 pixels)

2. **Read `mario.py`**
   - Study the `MarioIntent` dataclass (user desires)
   - Study the `MarioState` dataclass (actual state)
   - Understand the separation between intent and state

3. **Examine `world.py` and `physics/pipeline.py`**
   - See how the physics pipeline works
   - Each processor handles one aspect (gravity, friction, collisions)
   - Processors run in a specific order for correct physics

4. **Review `game.py`**
   - Understand the game loop: handle_events → update → draw
   - See the 60 FPS timing with `clock.tick(FPS)`
   - Note the display presentation pipeline

## Exercises

### Understanding the Code

1. **Trace a key press**: Follow arrow key from `handle_events()` to Mario moving
2. **Find the physics**: Look in `game/physics/` folder - each file does one thing!
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

## Computer Science Concepts

### State Machines (Mario's Brain!)

- Mario can be: idle, walking, running, jumping, or skidding
- Only one state at a time (can't be idle AND running)
- States change based on input and physics
- Like a flowchart that controls Mario's behavior

### The Game Loop (60 Times Per Second!)

```python
while game_is_running:
    handle_input()     # Check what keys are pressed
    update_physics()   # Move things, check collisions
    draw_everything()  # Show it on screen
```

### Why Bottom-Up Coordinates?

- In math class: y goes up (like our game!)
- In most computer graphics: y goes down
- We chose math-style because physics formulas make more sense

### How Animation Works

- Mario has different pictures for each frame
- We cycle through them to create movement
- Like a flipbook animation!

## Development Tools We Use

### Poetry (Package Manager)

- Manages all the libraries we need (like pygame)
- Creates a "virtual environment" (isolated Python setup)
- Run `poetry install` to get everything set up!

### Code Formatters (Make Code Pretty)

- **Black**: Auto-formats your code consistently
- **isort**: Organizes import statements
- **flake8**: Catches common mistakes
- **mypy**: Checks that variables have the right types

Just run `poetry run format` and it fixes everything!

## The Math Behind the Game

### Coordinates (Like Graph Paper!)

- Position (x, y) - Where Mario is on screen
- Velocity (vx, vy) - How fast Mario moves
- Acceleration (gravity) - Why Mario falls down
- It's just like plotting points in math class!

### Physics Made Simple

- **Gravity**: Mario falls at 400 pixels/second² (try changing it!)
- **Friction**: Mario slows down when you stop pressing keys
- **Jumping**: Gives Mario upward velocity to fight gravity
- The formula: `new_position = old_position + velocity × time`

## Next Steps After This Project

### Fun Things to Try

- Add power-ups (mushroom, fire flower)
- Create your own level designs
- Add sound effects and music
- Make enemies that move in patterns
- Design a boss battle!

### Skills to Learn Next

- **Pixel Art**: Try Aseprite or Piskel (free)
- **Level Design**: Study what makes Mario levels fun
- **Game Feel**: Why some games feel better to play
- **Simple AI**: Make enemies that chase or patrol

### Books for Young Game Developers

- **"Mission Python"** - Learn Python by coding a space adventure game
- **"Game Programming for Teens"** by Maneesh Sethi - Perfect for beginners
- **"Invent Your Own Computer Games with Python"** by Al Sweigart - Free online!

### YouTube Channels to Follow

- **Brackeys** (archived) - Unity tutorials for beginners
- **Code Monkey** - Game development made simple
- **Sebastian Lague** - Beautiful explanations of game concepts

### Free Online Resources

- **CodeCombat** - Learn Python by playing a game
- **Khan Academy** - Free programming courses
- **Unity Learn** - Free game development courses
- **GDevelop** - Make games without coding first

### Cool Things to Research

- How Mario's jump arc works (parabolas in math class!)
- Why 60 FPS makes games feel smooth
- How collision detection prevents walking through walls
- The history of platform games (Super Mario Bros, Sonic, etc.)

## Code Standards

This project follows:

- PEP 8 style guide
- Type annotations for all function signatures
- Docstrings for all classes and public methods
- Single responsibility principle
- Explicit over implicit

## Why the Code is Organized This Way

The code follows simple rules:

1. **Mario** only knows how to draw himself and express what he wants
2. **Physics Pipeline** figures out what actually happens (gravity, collisions)
3. **World** runs the physics pipeline and tells Mario the result
4. We always copy data before changing it (no surprises!)

This makes the code:

- **Easy to debug** (each file does one thing)
- **Easy to test** (test each part separately)
- **Easy to extend** (add new features without breaking old ones)

Remember: Good code is easy to understand, not clever and confusing!
