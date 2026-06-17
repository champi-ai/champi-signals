"""Champi Signals - Simple signal management extracted from Champi services.

This library provides signal management infrastructure with ABC for custom managers,
EventProcessor decorators, and enum setup utilities.
"""

__version__ = "0.2.0"
__author__ = "Divagnz"

# Signal bridge ABC
from .bridges import (
    SignalBridgeABC,
)

# Signal manager ABC and base class
# Enums and setup utilities
from .enums import (
    EnumSetup,
    ImgUIEventTypes,
    STTEventTypes,
    TTSEventTypes,
    make_event_types,
)
from .managers import (
    BaseSignalManager,
    SignalManagerABC,
)

# Event processor from champi services
from .processors import (
    EventProcessor,
)

# Main exports
__all__ = [
    # Signal bridge
    "SignalBridgeABC",
    # Signal manager infrastructure
    "SignalManagerABC",
    "BaseSignalManager",
    # Event processor
    "EventProcessor",
    # Enums
    "STTEventTypes",
    "TTSEventTypes",
    "ImgUIEventTypes",
    "EnumSetup",
    "make_event_types",
]
