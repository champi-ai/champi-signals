# Champi Signals Examples

This directory contains practical examples demonstrating various features of the champi-signals library.

## Running the Examples

First, install the library with dev dependencies:

```bash
uv pip install -e ".[dev]"
```

Then run any example:

```bash
python examples/basic_example.py
python examples/event_processor_example.py
python examples/custom_enums_example.py
python examples/async_example.py
```

## Examples Overview

### 1. Basic Example (`basic_example.py`)

**Demonstrates:**
- Creating a custom signal manager
- Setting up signals with predefined enums
- Connecting receivers to signals
- Emitting events
- Connecting multiple receivers to the same signal

**Key Concepts:**
- Signal manager singleton pattern
- Using property setters to connect receivers
- Event emission with `send()`

### 2. Event Processor Example (`event_processor_example.py`)

**Demonstrates:**
- Using `@EventProcessor.emits_event` decorator
- Automatic START/FINISH/ERROR event emission
- State variable tracking with `data` parameter
- Custom metadata in events
- Metaclass signal manager extraction

**Key Concepts:**
- Service `Meta` class with `signal_manager` and `event_type`
- Automatic event emission around method execution
- Variable state capture before and after execution
- Error event emission on exceptions

### 3. Custom Enums Example (`custom_enums_example.py`)

**Demonstrates:**
- Creating custom service enums with `EnumSetup`
- Using `setup_service_enums()` for complete enum setup
- Integrating custom enums with signal managers
- Service-specific event types

**Key Concepts:**
- `EnumSetup.setup_service_enums()` for creating multiple enums
- Dynamic enum creation for any service
- Custom event type categories

### 4. Async Example (`async_example.py`)

**Demonstrates:**
- Using `@EventProcessor.emits_event` with async methods
- Periodic variable monitoring with `@EventProcessor.periodic_emit`
- Async error handling
- Concurrent async operations

**Key Concepts:**
- Automatic async/await support in decorators
- Progress monitoring during long-running operations
- PROGRESS events emitted at intervals
- Concurrent event processing

## Common Patterns

### Creating a Signal Manager

```python
from champi_signals import BaseSignalManager, STTEventTypes

class MySignalManager(BaseSignalManager):
    def __init__(self):
        super().__init__()
        if not self._signals_initialized:
            self.setup_custom_signals({
                'lifecycle': STTEventTypes,
                'processing': STTEventTypes,
            })
```

### Connecting Receivers

```python
signals = MySignalManager()

def my_receiver(sender, **kwargs):
    print(f"Event: {kwargs}")

# Connect using property setter
signals.processing = my_receiver
```

### Using EventProcessor

```python
from champi_signals import EventProcessor

class MyService:
    class Meta:
        event_type = "processing"
        signal_manager = MySignalManager()

    @EventProcessor.emits_event(data=['status'])
    def do_something(self):
        self.status = "done"
```

### Creating Custom Enums

```python
from champi_signals import EnumSetup

enums = EnumSetup.setup_service_enums('MyService', {
    'event_types': ['lifecycle', 'processing'],
    'lifecycle': ['idle', 'running', 'stopped'],
    'processing': ['start', 'process', 'finish']
})
```

## Event Structure

Events emitted by the library have the following structure:

```python
{
    'event_type': 'processing',      # Signal category
    'sub_event': 'METHOD_START',     # Specific event (METHOD_START/FINISH/ERROR/PROGRESS)
    'data': {                        # Event data
        'status': 'ready',           # Tracked variables
        'timestamp': 12345.67,       # Timestamp (for async)
        'success': True,             # Success flag (FINISH events)
        'error': 'message',          # Error info (ERROR events)
        'duration_seconds': 1.5,     # Duration (FINISH/ERROR events)
        # ... custom metadata
    }
}
```

## Tips

1. **Singleton Pattern**: Signal managers are singletons per class, ensuring global coordination
2. **Variable Tracking**: Use `data=['var1', 'var2']` to track variable state changes
3. **Class Variables**: Prefix with `cls.` to track class variables (e.g., `data=['cls.count']`)
4. **Async Support**: Decorators automatically detect and handle async methods
5. **Error Handling**: Errors are emitted as events but still propagate (re-raised)
6. **Progress Monitoring**: Use `@EventProcessor.periodic_emit` for long-running async operations

## Next Steps

After reviewing these examples:

1. Read the main [README.md](../README.md) for API documentation
2. Check out the [tests](../tests/) for more usage patterns
3. Review the source code in [src/champi_signals/](../src/champi_signals/)
