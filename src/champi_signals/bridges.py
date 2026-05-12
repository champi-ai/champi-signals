"""Signal bridge abstract base class for connecting blinker signals to external transports."""

from abc import ABC, abstractmethod

from champi_signals.managers import BaseSignalManager


class SignalBridgeABC(ABC):
    """Abstract base class for bridging blinker signals to external transports.

    Subclasses implement the transport-specific connect/disconnect and
    async start/stop lifecycle, enabling champi-ipc and other consumers
    to bind a ``BaseSignalManager`` to any message-passing backend.
    """

    _manager: BaseSignalManager | None = None

    @abstractmethod
    def connect(self, signal_manager: BaseSignalManager) -> None:
        """Bind this bridge to a signal manager.

        Args:
            signal_manager: The ``BaseSignalManager`` instance whose signals
                            should be forwarded over the transport.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Unbind this bridge from its signal manager."""
        ...

    @abstractmethod
    async def start(self) -> None:
        """Start the underlying transport (open sockets, threads, etc.)."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the underlying transport and release resources."""
        ...

    @property
    def is_connected(self) -> bool:
        """Return ``True`` if a signal manager is currently bound."""
        return self._manager is not None
