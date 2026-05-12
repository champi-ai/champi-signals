# champi-signals

Signal management and event processing library for Champi voice assistant services.

## Overview

`champi-signals` provides signal management infrastructure used across the Champi service
ecosystem:

- `BaseSignalManager` — base class for building singleton signal managers
- `SignalBridgeABC` — abstract base for cross-process signal bridge implementations
- `EventProcessor` — decorator for registering typed event handler functions
- `STTEventTypes` / `TTSEventTypes` — built-in string-value event type enums
- `ImgUIEventTypes` — integer event codes for the ImgUI rendering service
- `EnumSetup` — utility class for creating string-value enum registries
- `make_event_types` — factory for generating integer-keyed event enums from a spec dict

## Installation

```bash
pip install champi-signals
```

For development:

```bash
git clone https://github.com/champi-ai/champi-signals.git
cd champi-signals
uv sync --extra dev
```

## Quick start

```python
from champi_signals import (
    BaseSignalManager,
    STTEventTypes,
    ImgUIEventTypes,
    make_event_types,
)

# Use a pre-defined IntEnum for ImgUI events
print(ImgUIEventTypes.TOOL_CALL_START)  # 100

# Generate a custom IntEnum from a spec
MyEvents = make_event_types("MyEvents", {
    "PROCESS": ["START", "FINISH", "ERROR"],
    "RENDER":  ["BEGIN", "END"],
})
print(MyEvents.PROCESS_START)  # 1

# Build a signal manager wired to enum members
class MyManager(BaseSignalManager):
    def __init__(self):
        super().__init__()
        self.setup_custom_signals({"stt": STTEventTypes})

manager = MyManager()
manager.stt.connect(lambda sender, **kw: print("signal:", kw))
```
