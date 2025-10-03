"""Tests for signal managers."""

import pytest
from champi_signals import BaseSignalManager, SignalManagerABC
from enum import Enum


class TestSignalManagerABC:
    """Tests for SignalManagerABC."""

    def test_is_abstract(self):
        """Test that SignalManagerABC cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SignalManagerABC()


class TestBaseSignalManager:
    """Tests for BaseSignalManager."""

    def test_singleton_pattern(self):
        """Test that BaseSignalManager follows singleton pattern."""
        manager1 = BaseSignalManager()
        manager2 = BaseSignalManager()
        assert manager1 is manager2

    def test_initial_state(self):
        """Test initial state of signal manager."""
        manager = BaseSignalManager()
        assert hasattr(manager, "signals")
        assert isinstance(manager.signals, dict)

    def test_setup_custom_signals(self, signal_config):
        """Test setting up custom signals."""
        manager = BaseSignalManager()
        manager.setup_custom_signals(signal_config)

        assert "lifecycle" in manager.signals
        assert "processing" in manager.signals

    def test_signal_property_getter(self, signal_config):
        """Test that signals can be accessed as properties."""
        manager = BaseSignalManager()
        manager.setup_custom_signals(signal_config)

        lifecycle_signal = manager.lifecycle
        assert lifecycle_signal is not None

    def test_signal_property_setter_connects_receiver(
        self, signal_config, event_receiver, received_events
    ):
        """Test that setting a signal property connects a receiver."""
        manager = BaseSignalManager()
        manager.setup_custom_signals(signal_config)

        # Connect receiver using property setter
        manager.lifecycle = event_receiver

        # Emit event
        manager.lifecycle.send(
            event_type="lifecycle", sub_event="TEST", data={"test": "data"}
        )

        # Verify receiver was called
        assert len(received_events) == 1
        assert received_events[0]["event_type"] == "lifecycle"
        assert received_events[0]["sub_event"] == "TEST"
        assert received_events[0]["data"] == {"test": "data"}

    def test_get_signals(self, signal_config):
        """Test getting all signals."""
        manager = BaseSignalManager()
        manager.setup_custom_signals(signal_config)

        signals = manager.get_signals()
        assert len(signals) == 2

    def test_multiple_receivers(self, signal_config):
        """Test that multiple receivers can be connected."""
        manager = BaseSignalManager()
        manager.setup_custom_signals(signal_config)

        received1 = []
        received2 = []

        def receiver1(sender, **kwargs):
            received1.append(kwargs)

        def receiver2(sender, **kwargs):
            received2.append(kwargs)

        manager.lifecycle = receiver1
        manager.lifecycle = receiver2

        manager.lifecycle.send(event_type="test")

        assert len(received1) == 1
        assert len(received2) == 1

    def test_custom_signal_with_empty_enum(self):
        """Test setup with custom configuration."""

        class TestEnum(Enum):
            TEST_VALUE = "test"

        manager = BaseSignalManager()
        # Should work with any enum
        manager.setup_custom_signals({"test": TestEnum})
        assert "test" in manager.signals


class TestCustomSignalManager:
    """Tests for custom signal manager implementations."""

    def test_custom_manager_singleton(self, signal_config):
        """Test that custom managers also follow singleton pattern."""

        class CustomSignalManager(BaseSignalManager):
            def __init__(self):
                super().__init__()
                if not self._signals_initialized:
                    self.setup_custom_signals(signal_config)

        manager1 = CustomSignalManager()
        manager2 = CustomSignalManager()
        assert manager1 is manager2

    def test_custom_manager_signals(self):
        """Test custom manager with specific signals."""

        class TTSEventTypes(Enum):
            LIFECYCLE_EVENT = "lifecycle_event"
            MODEL_EVENT = "model_event"

        # Create a unique manager class to avoid singleton conflicts
        class TTSSignalManager2(BaseSignalManager):
            _instance = None
            _signals_initialized = False

            def __init__(self):
                if type(self)._instance is None:
                    type(self)._instance = self
                if not type(self)._signals_initialized:
                    self.signals = {}
                    self._class_signals = {}
                    self.setup_custom_signals(
                        {"lifecycle": TTSEventTypes, "model": TTSEventTypes}
                    )
                    type(self)._signals_initialized = True

        manager = TTSSignalManager2()
        assert hasattr(manager, "lifecycle")
        assert hasattr(manager, "model")
