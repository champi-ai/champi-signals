# Integration Guide

`champi-signals` is the shared signal bus used by all Champi services.  Each service
creates a typed signal manager by subclassing `BaseSignalManager` and wiring it to
an enum that describes that service's event vocabulary.

## champi-stt

The speech-to-text service uses `STTEventTypes` to broadcast lifecycle, model,
processing, and telemetry events over its signal manager.

```python
from champi_signals import BaseSignalManager, STTEventTypes

class STTSignalManager(BaseSignalManager):
    def __init__(self):
        super().__init__()
        self.setup_custom_signals({
            "lifecycle":  STTEventTypes,
            "model":      STTEventTypes,
            "processing": STTEventTypes,
            "telemetry":  STTEventTypes,
        })
```

## champi-tts

The text-to-speech service mirrors the same pattern with `TTSEventTypes`.

```python
from champi_signals import BaseSignalManager, TTSEventTypes

class TTSSignalManager(BaseSignalManager):
    def __init__(self):
        super().__init__()
        self.setup_custom_signals({
            "lifecycle":  TTSEventTypes,
            "processing": TTSEventTypes,
        })
```

## champi-imgui

The ImgUI rendering service uses `ImgUIEventTypes` (an `IntEnum`) so that event
codes can be compared numerically and serialised as plain integers over IPC.

```python
from champi_signals import BaseSignalManager, ImgUIEventTypes

class ImgUISignalManager(BaseSignalManager):
    def __init__(self):
        super().__init__()
        self.setup_custom_signals({"imgui": ImgUIEventTypes})

manager = ImgUISignalManager()
manager.imgui.send("canvas", event=ImgUIEventTypes.CANVAS_UPDATE)
```

## champi-ipc

The IPC layer uses `make_event_types` to generate a custom `IntEnum` from a
configuration dict, keeping the event vocabulary co-located with the IPC channel
definition:

```python
from champi_signals import make_event_types

IPCEvents = make_event_types("IPCEvents", {
    "CHANNEL": ["OPEN", "CLOSE", "ERROR"],
    "MESSAGE": ["SEND", "RECEIVE", "DROP"],
})
```
