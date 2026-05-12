"""Tests for SignalBridgeABC."""

import pytest

from champi_signals import BaseSignalManager, SignalBridgeABC


class ConcreteStubBridge(SignalBridgeABC):
    """Concrete stub that records method calls for assertion."""

    def __init__(self):
        self.connect_calls: list[BaseSignalManager] = []
        self.disconnect_calls: int = 0
        self.start_calls: int = 0
        self.stop_calls: int = 0

    def connect(self, signal_manager: BaseSignalManager) -> None:
        self._manager = signal_manager
        self.connect_calls.append(signal_manager)

    def disconnect(self) -> None:
        self._manager = None
        self.disconnect_calls += 1

    async def start(self) -> None:
        self.start_calls += 1

    async def stop(self) -> None:
        self.stop_calls += 1


class TestSignalBridgeABCAbstract:
    """Verify that SignalBridgeABC cannot be instantiated directly."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            SignalBridgeABC()  # type: ignore[abstract]

    def test_partial_implementation_raises(self):
        """A subclass missing any abstract method must still raise."""

        class PartialBridge(SignalBridgeABC):
            def connect(self, signal_manager: BaseSignalManager) -> None: ...
            def disconnect(self) -> None: ...
            async def start(self) -> None: ...
            # stop is missing

        with pytest.raises(TypeError):
            PartialBridge()  # type: ignore[abstract]


class TestConcreteStubBridge:
    """Tests for the concrete stub covering all SignalBridgeABC behaviour."""

    def test_is_connected_false_initially(self):
        bridge = ConcreteStubBridge()
        assert bridge.is_connected is False

    def test_connect_sets_manager_and_is_connected(self):
        bridge = ConcreteStubBridge()
        manager = BaseSignalManager()

        bridge.connect(manager)

        assert bridge.is_connected is True
        assert bridge.connect_calls == [manager]

    def test_disconnect_clears_manager(self):
        bridge = ConcreteStubBridge()
        manager = BaseSignalManager()

        bridge.connect(manager)
        bridge.disconnect()

        assert bridge.is_connected is False
        assert bridge.disconnect_calls == 1

    def test_connect_then_disconnect_then_reconnect(self):
        bridge = ConcreteStubBridge()
        manager = BaseSignalManager()

        bridge.connect(manager)
        bridge.disconnect()
        bridge.connect(manager)

        assert bridge.is_connected is True
        assert len(bridge.connect_calls) == 2
        assert bridge.disconnect_calls == 1

    async def test_start_increments_call_count(self):
        bridge = ConcreteStubBridge()
        await bridge.start()
        assert bridge.start_calls == 1

    async def test_stop_increments_call_count(self):
        bridge = ConcreteStubBridge()
        await bridge.stop()
        assert bridge.stop_calls == 1

    async def test_start_stop_lifecycle(self):
        bridge = ConcreteStubBridge()
        manager = BaseSignalManager()

        bridge.connect(manager)
        await bridge.start()
        await bridge.stop()
        bridge.disconnect()

        assert bridge.start_calls == 1
        assert bridge.stop_calls == 1
        assert bridge.is_connected is False

    async def test_multiple_start_stop_calls(self):
        bridge = ConcreteStubBridge()

        await bridge.start()
        await bridge.start()
        await bridge.stop()
        await bridge.stop()

        assert bridge.start_calls == 2
        assert bridge.stop_calls == 2


class TestSignalBridgeABCExported:
    """Verify the class is reachable from the top-level package."""

    def test_exported_from_package(self):
        import champi_signals

        assert hasattr(champi_signals, "SignalBridgeABC")
        assert champi_signals.SignalBridgeABC is SignalBridgeABC
