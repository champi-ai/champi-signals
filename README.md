# Champi Signals

**Signal management framework with ABC for custom managers**

This library provides a signal management framework with Abstract Base Classes for creating custom signal managers, EventProcessor decorators that extract signal managers from service metaclasses, and utilities for setting up custom enums.

## Installation

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

## Usage

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

- **Metaclass Signal Extraction**: EventProcessor automatically extracts signal managers from service `Meta.signal_manager`
- **Singleton Pattern**: All signal managers follow singleton pattern for global coordination
- **Dynamic Signal Setup**: Create signals dynamically using `setup_custom_signals()`
- **Custom Enums**: Generate service-specific enums with `EnumSetup`

## Examples

- `examples/simple_example.py` - Basic usage with custom signal managers
- `examples/metaclass_example.py` - Advanced metaclass signal manager extraction

## License

MIT License - same as Champi project.