# champi-signals v0.2.0 — Public API Spec

## Overview

This spec defines the **consumer-facing (public API) surface** for champi-signals v0.2.0. It covers every importable symbol, decorator, enum, CLI command, and integration contract that downstream packages (champi-stt, champi-tts, champi-imgui, champi-ipc) depend on.

Current version: **0.1.0** (stable, released on PyPI).  
Target version: **0.2.0** (this spec).

---

## Section 1 — Existing Public API (must remain backward-compatible)

```python
from champi_signals import (
    BaseSignalManager,   # Extend to create custom signal manager
    EventProcessor,      # Decorator for automatic event emission
    STTEventTypes,       # Pre-defined STT event enum
    TTSEventTypes,       # Pre-defined TTS event enum
    EnumSetup,           # Utility for creating custom enums
)
```

All symbols above are exported from `src/champi_signals/__init__.py`. No breaking changes permitted in v0.2.0.

---

## Section 2 — New Public API (v0.2.0 additions)

### 2.1 `SignalBridgeABC` — IPC bridge interface

**Purpose**: Abstract interface that champi-ipc will implement to bridge blinker signals to shared memory. Defined in champi-signals so downstream code depends only on this library, not on champi-ipc directly.

```python
from champi_signals import SignalBridgeABC

class SignalBridgeABC(ABC):
    """Abstract base for bridging blinker signals to an external transport."""

    @abstractmethod
    def connect(self, signal_manager: BaseSignalManager) -> None:
        """Attach this bridge to a signal manager."""

    @abstractmethod
    def disconnect(self) -> None:
        """Detach and release resources."""

    @abstractmethod
    async def start(self) -> None:
        """Start the bridge (background tasks, threads, etc.)."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop the bridge gracefully."""
```

**Export**: `from champi_signals import SignalBridgeABC`

---

### 2.2 Enhanced `EventProcessor` — class-level decoration and context managers

**New capability 1**: Decorate an entire class so all public methods emit events without per-method decoration.

```python
@EventProcessor.emits_all_events(data=['status'])
class ReadingService:
    class Meta:
        event_type = "reading"
        signal_manager = TTSSignalManager()
    ...
```

**New capability 2**: Context manager form for imperative code:

```python
async with EventProcessor.context(signal_manager, "reading", data={'text': text}):
    await synthesize(text)
```

**Backward compatible**: existing `@EventProcessor.emits_event(data=[...])` method decorator unchanged.

---

### 2.3 `ImgUIEventTypes` — MCP event enum

**Purpose**: champi-imgui needs event types for MCP tool invocations. Add a pre-defined `ImgUIEventTypes` enum alongside `STTEventTypes` and `TTSEventTypes`.

```python
from champi_signals import ImgUIEventTypes

class ImgUIEventTypes(IntEnum):
    TOOL_CALL_START   = 100
    TOOL_CALL_FINISH  = 101
    TOOL_CALL_ERROR   = 102
    CANVAS_UPDATE     = 110
    WIDGET_CREATE     = 120
    WIDGET_DELETE     = 121
    RENDER_FRAME      = 130
```

**Export**: `from champi_signals import ImgUIEventTypes`

---

### 2.4 `make_event_types()` — generic factory

**Purpose**: Programmatic creation of event-type enums from a declarative dict (generalises `EnumSetup`).

```python
from champi_signals import make_event_types

MyEvents = make_event_types("MyEvents", {
    "PROCESS": ["START", "FINISH", "ERROR"],
    "LOAD":    ["START", "FINISH", "ERROR"],
})
# Generates: MyEvents.PROCESS_START=0, PROCESS_FINISH=1, PROCESS_ERROR=2, ...
```

**Export**: `from champi_signals import make_event_types`

---

## Section 3 — CLI

No CLI is planned for champi-signals itself. CLI tooling for IPC belongs in champi-ipc.

---

## Section 4 — API Contract for Downstream

| Consumer | Uses |
|---|---|
| champi-stt | `BaseSignalManager`, `EventProcessor`, `STTEventTypes` |
| champi-tts | `BaseSignalManager`, `EventProcessor`, `TTSEventTypes`, `EventProcessor.context` (new) |
| champi-imgui | `BaseSignalManager`, `ImgUIEventTypes` (new), `SignalBridgeABC` (new) |
| champi-ipc | `SignalBridgeABC` (new), `BaseSignalManager` |

---

## Section 5 — Packaging & Distribution

- Package name: `champi-signals` (unchanged)
- PyPI: published via GitHub Actions trusted-publisher on version tag
- Minimum Python: 3.12
- Extras: none planned

---

## Section 6 — Documentation

- mkdocs-material site auto-built from docstrings (mkdocstrings-python)
- Published to GitHub Pages on every release tag
- Sections: Getting Started, API Reference, Integration Guide, Changelog
