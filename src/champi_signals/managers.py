"""Signal managers extracted from Champi services."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum

from blinker import Signal


class SignalManagerABC(ABC):
    """Abstract base class for signal managers."""

    @abstractmethod
    def setup_custom_signals(self, signal_config: dict[str, type[Enum]]) -> None:
        """Setup custom signals based on provided enum configuration.

        Args:
            signal_config: Dictionary mapping signal names to their enum types
                          e.g., {'lifecycle': MyLifecycleEnum, 'processing': MyProcessingEnum}
        """
        pass


class BaseSignalManager(SignalManagerABC):
    """Base signal manager with common functionality."""

    _instance = None
    _signals_initialized = False

    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize singleton instance only once"""
        if not self._signals_initialized:
            self.signals: dict[str, Signal] = {}
            self._class_signals: dict[str, Signal] = {}
            type(self)._signals_initialized = True

    def get_signals(self) -> list[Signal]:
        """Get all registered signals."""
        return list(self.signals.values())

    def setup_custom_signals(self, signal_config: dict[str, type[Enum]]) -> None:
        """Setup custom signals based on provided enum configuration.

        Args:
            signal_config: Dictionary mapping signal names to their enum types
        """
        for signal_name, enum_type in signal_config.items():
            # Get the first enum value as the signal identifier
            signal_identifier = list(enum_type)[0].value if enum_type else signal_name
            signal_obj = Signal(signal_identifier)

            # Store the signal
            self.signals[signal_name] = signal_obj
            self._class_signals[f"_{signal_name}_signal"] = signal_obj

            # Create property accessor dynamically
            self._create_signal_property(signal_name, signal_obj)

    def _create_signal_property(self, signal_name: str, signal_obj: Signal) -> None:
        """Create getter/setter properties for a signal."""

        def getter(_self):
            return signal_obj

        def setter(_self, receiver: Callable):
            signal_obj.connect(receiver)

        # Set the property on the class
        setattr(type(self), signal_name, property(getter, setter))
