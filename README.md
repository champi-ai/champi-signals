# Champi Signals

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Signal management framework with ABC for custom managers**

A lightweight, flexible signal management library for Python applications. Built on top of [blinker](https://github.com/pallets-eco/blinker), it provides abstract base classes for creating custom signal managers, EventProcessor decorators for automatic event emission, and utilities for setting up custom enums.

## Features

- 🎯 **Abstract Base Classes** - Clean interface for building custom signal managers
- 🔄 **Event Processing** - Automatic START/FINISH/ERROR event emission with decorators
- 🔗 **Singleton Pattern** - Global signal coordination across your application
- ⚡ **Async Support** - Full support for both sync and async methods
- 📊 **State Tracking** - Automatic variable state capture before/after execution
- 🎨 **Custom Enums** - Dynamic enum generation for service-specific events
- 📈 **Progress Monitoring** - Periodic variable emission for long-running operations
- 🔍 **Type Safe** - Full type hints with py.typed marker

## Installation

### From Local Path (Development)

Add to your `pyproject.toml`:

```toml
[tool.uv.sources]
champi-signals = { path = "../libraries/champi_signals", editable = true }

[project]
dependencies = [
    "champi-signals",
    # ... other dependencies
]
```

### From PyPI (Coming Soon)

```bash
pip install champi-signals
# or
uv pip install champi-signals
```

## Quick Start

### Creating Custom Signal Managers

```python
from champi_signals import BaseSignalManager, STTEventTypes

class STTSignalManager(BaseSignalManager):
    """Custom STT Signal Manager"""

    def __init__(self):
        super().__init__()
        # Setup signals using existing or custom enums
        self.setup_custom_signals({
            'lifecycle': STTEventTypes,
            'model': STTEventTypes,
            'processing': STTEventTypes,
            'telemetry': STTEventTypes
        })

# Use the signal manager (singleton pattern)
signals = STTSignalManager()

# Connect receivers
def handle_stt_events(sender, **kwargs):
    print(f"STT Event: {kwargs}")

signals.processing = handle_stt_events  # Connects receiver

# Emit events
signals.processing.send(
    event_type="processing",
    sub_event="TRANSCRIPTION_COMPLETE",
    data={"text": "hello world"}
)
```

### EventProcessor with Metaclass Signal Manager

```python
from champi_signals import EventProcessor

class STTService:
    def __init__(self):
        self.status = "uninitialized"
        self.transcription_count = 0

    class Meta:
        event_type = "processing"  # Which signal to use
        signal_manager = STTSignalManager()  # Custom signal manager instance

    @EventProcessor.emits_event(data=['status', 'transcription_count'])
    def initialize(self):
        """Automatically emits INITIALIZE_START and INITIALIZE_FINISH events"""
        self.status = "ready"
        return True

    @EventProcessor.emits_event(data=['transcription_count'])
    async def transcribe(self, text: str):
        """Automatically emits TRANSCRIBE_START/FINISH/ERROR events"""
        self.transcription_count += 1
        return f"Transcribed: {text}"
```

### Custom Enum Setup

```python
from champi_signals import EnumSetup

# Create custom enums for a new service
nlp_enums = EnumSetup.setup_service_enums('NLP', {
    'event_types': ['lifecycle', 'processing', 'analysis'],
    'lifecycle': ['idle', 'loading', 'ready', 'analyzing'],
    'processing': ['tokenize', 'parse', 'extract', 'classify']
})

# Use with custom signal manager
class NLPSignalManager(BaseSignalManager):
    def __init__(self):
        super().__init__()
        self.setup_custom_signals({
            'lifecycle': nlp_enums['EventTypes'],
            'processing': nlp_enums['EventTypes'],
            'analysis': nlp_enums['EventTypes']
        })
```

## What's Included

- **SignalManagerABC** - Abstract base class for signal managers
- **BaseSignalManager** - Base implementation with singleton pattern and custom signal setup
- **EventProcessor** - Decorators that extract signal managers from service metaclasses
- **STTEventTypes/TTSEventTypes** - Pre-defined event enums
- **EnumSetup** - Utility for creating custom service enums

## Key Features

### Metaclass Signal Extraction
EventProcessor automatically extracts signal managers from service `Meta.signal_manager`

### Singleton Pattern
All signal managers follow singleton pattern for global coordination

### Dynamic Signal Setup
Create signals dynamically using `setup_custom_signals()`

### Custom Enums
Generate service-specific enums with `EnumSetup`

### Async Support
Decorators automatically detect and handle async methods with proper event timing

### Error Handling
Exceptions are captured and emitted as ERROR events while still being re-raised

## Examples

Check out the [examples/](examples/) directory for comprehensive examples:

- [`basic_example.py`](examples/basic_example.py) - Basic signal manager usage
- [`event_processor_example.py`](examples/event_processor_example.py) - EventProcessor with metaclass
- [`custom_enums_example.py`](examples/custom_enums_example.py) - Custom enum creation
- [`async_example.py`](examples/async_example.py) - Async event processing with progress monitoring

Run examples:
```bash
python examples/basic_example.py
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/Divagnz/champi-signals.git
cd champi-signals

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=champi_signals --cov-report=html

# Run specific test file
pytest tests/test_managers.py -v
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

### Making Commits

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for conventional commits:

```bash
# Make a commit
cz commit

# Or use conventional commit format manually
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update README"
```

## Project Structure

```
champi_signals/
├── src/
│   └── champi_signals/
│       ├── __init__.py      # Main exports
│       ├── managers.py      # Signal manager ABC and base class
│       ├── processors.py    # Event processor decorators
│       ├── enums.py         # Event type enums and setup utilities
│       └── py.typed         # Type checking marker
├── tests/                   # Comprehensive test suite
│   ├── test_managers.py
│   ├── test_processors.py
│   └── test_enums.py
├── examples/                # Practical examples
│   ├── basic_example.py
│   ├── event_processor_example.py
│   ├── custom_enums_example.py
│   └── async_example.py
├── pyproject.toml          # Project configuration
├── LICENSE                 # MIT License
├── README.md               # This file
└── CHANGELOG.md            # Version history
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with conventional commits
4. Run tests and linting
5. Push to your branch
6. Open a Pull Request

## Dependencies

- Python >= 3.12
- [blinker](https://github.com/pallets-eco/blinker) >= 1.7.0 - Signal/event system
- [loguru](https://github.com/Delgan/loguru) >= 0.7.0 - Logging (optional, for examples)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of the excellent [blinker](https://github.com/pallets-eco/blinker) library
- Inspired by signal patterns in the Champi voice assistant project
- Follows [Keep a Changelog](https://keepachangelog.com/) for versioning

## Links

- **Documentation**: [README.md](README.md) and [examples/](examples/)
- **Source Code**: [GitHub](https://github.com/Divagnz/champi-signals)
- **Issue Tracker**: [GitHub Issues](https://github.com/Divagnz/champi-signals/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

Made with ❤️ for the Champi project
