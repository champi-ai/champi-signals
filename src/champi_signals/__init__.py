"""Champi Signals - Simple signal management extracted from Champi services.

This library provides signal management infrastructure with ABC for custom managers,
EventProcessor decorators, and enum setup utilities.
"""

__version__ = "0.1.0"
__author__ = "Divagnz"

# Signal manager ABC and base class
# Enums and setup utilities
from .enums import (
    EnumSetup,
    STTEventTypes,
    TTSEventTypes,
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
    # Signal manager infrastructure
    "SignalManagerABC",
    "BaseSignalManager",
    # Event processor
    "EventProcessor",
    # Enums
    "STTEventTypes",
    "TTSEventTypes",
    "EnumSetup",
]
