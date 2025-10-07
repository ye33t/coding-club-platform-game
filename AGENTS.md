# Repository Guidelines

## Project Structure & Module Organization

- `game/` holds runtime code; key subpackages include `physics/` for the pipeline processors, `states/` for Mario state transitions, and `terrain/` plus `levels/` for tile data.
- Art, level YAML, and runtime configs live under `game/assets/`; update these in tandem with code changes so assets remain in sync.
- Reusable scripts (`main.py`, `sprite_extractor.py`, `format.py`) sit at the repo root, while automated checks belong in `format.py`.
- Tests reside in `tests/`, mirroring the package layout (for example, physics tests live in `tests/physics/`); add new suites alongside the feature they cover.

## Build, Test, and Development Commands

- `poetry install`: set up the virtualenv and install runtime plus dev dependencies.
- `poetry run game`: launch the playable demo via `main:main`.
- `poetry run pytest` (or `poetry run test`): execute the automated test suite defined in `pytest.ini`.
- `poetry run format`: run the formatting and linting pipeline (isort → black → flake8 → mypy) defined in `format.py`.

## Coding Style & Naming Conventions

- Python 3.13 is the target; rely on type hints and dataclasses for new domain objects.
- Black enforces an 88-character line length, and imports must remain sorted via isort’s Black profile; avoid manual tweaks that fight these tools.
- Follow PEP 8 naming: modules and assets use lowercase_with_underscores, classes use `CamelCase`, and constants (see `game/constants.py`) use `UPPER_SNAKE_CASE`.
- Keep physics processors small and single-purpose; add a docstring explaining new pipeline steps or state transitions when behavior is non-obvious.

## Testing Guidelines

- Pytest discovers files matching `tests/test_*.py`; mirror the package path and name test functions `test_<behavior>()`.
- Run `poetry run pytest --cov=game` to gauge coverage when touching core gameplay or physics logic; prefer scenario-driven tests that validate the full pipeline.
- When adding assets, include smoke tests that load the new resources to catch missing files early.

## Commit & Pull Request Guidelines

- Follow Conventional Commits (`feat:`, `fix:`, `chore:`, etc.), matching the existing Git history.
- Keep commits focused: code, assets, and tests for a feature should land together with updated fixtures.
- Before opening a PR, run `poetry run format` and the full test suite; document behavioral changes with short clips or screenshots when gameplay visibly shifts.
- PR descriptions should outline the motivation, list key changes, link any tracked issues, and call out follow-up work or risks.
