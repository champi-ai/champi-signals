# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-17

### Added

- **IPC Signal Bridge**
  - `SignalBridgeABC` — Abstract base class for bridging blinker signals to external transports
  - Lifecycle interface: `connect()`, `disconnect()`, `start()`, `stop()`, `is_connected`

- **Enhanced EventProcessor**
  - `EventProcessor.emits_all_events()` — Class decorator that applies `emits_event` to every public, non-dunder method on a class
  - `EventProcessor.context()` — Async context manager emitting `START`/`FINISH`/`ERROR` events around arbitrary code blocks

- **Enum Expansion**
  - `ImgUIEventTypes` — Integer event type codes for ImgUI service (tool calls, canvas updates, widgets, render frames)
  - `make_event_types()` — Generate an `IntEnum` from a declarative spec dict with sequential values

- **Documentation**
  - MkDocs Material documentation site with mkdocstrings-python for API reference
  - GitHub Pages deployment via dedicated `docs.yml` workflow

- **CI / Infrastructure**
  - `docs.yml` — deploys MkDocs to GitHub Pages on push to `main`
  - `release.yml` — builds package and creates a GitHub Release on `v*.*.*` tags
  - All third-party GitHub Actions pinned to immutable commit SHAs

## [0.1.0] - 2025-10-03

### Added

- **Signal Management Framework**
  - `SignalManagerABC` - Abstract base class for signal managers
  - `BaseSignalManager` - Base implementation with singleton pattern
  - Dynamic signal setup via `setup_custom_signals()` method
  - Property-based signal access and receiver connection

- **Event Processing**
  - `EventProcessor` class with decorators for automatic event emission
  - `@EventProcessor.emits_event` - Emits START/FINISH/ERROR events around method execution
  - `@EventProcessor.periodic_emit` - Monitors variables during async execution
  - Automatic async/await support
  - State variable tracking with `data` parameter
  - Custom metadata support in events
  - Metaclass-based signal manager extraction from service `Meta` class

- **Enum Utilities**
  - Pre-defined `STTEventTypes` and `TTSEventTypes` enums
  - `EnumSetup` class for creating custom service enums
  - `create_event_types()` - Create event type enums
  - `create_lifecycle_events()` - Create lifecycle event enums
  - `create_processing_events()` - Create processing event enums
  - `setup_service_enums()` - Setup complete enum suite for services

- **Developer Tools**
  - Comprehensive test suite with pytest
  - Ruff configuration for linting and formatting
  - MyPy configuration for type checking
  - Pre-commit hooks configuration
  - Commitizen for conventional commits
  - Example scripts demonstrating all features

- **Documentation**
  - Comprehensive README with usage examples
  - API documentation in docstrings
  - Examples directory with 4 practical examples
  - Type hints throughout the codebase
  - PEP 561 support with py.typed marker

- **Build & Distribution**
  - Python 3.12+ support
  - Hatchling build backend
  - Dependencies: blinker>=1.7.0, loguru>=0.7.0
  - MIT License

### Features

- **Singleton Pattern**: All signal managers follow singleton pattern for global coordination
- **Flexible Signal Setup**: Create signals dynamically using any Enum type
- **Dual Sync/Async Support**: Decorators automatically handle both sync and async methods
- **Error Handling**: Exceptions are captured and emitted as ERROR events while still propagating
- **Progress Monitoring**: Track long-running async operations with periodic variable emission
- **Type Safety**: Full type hints and py.typed marker for type checkers

[Unreleased]: https://github.com/champi-ai/champi-signals/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/champi-ai/champi-signals/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/champi-ai/champi-signals/releases/tag/v0.1.0
