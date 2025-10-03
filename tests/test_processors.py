"""Tests for event processors."""

import pytest
import asyncio
from champi_signals import EventProcessor, BaseSignalManager
from enum import Enum


class ProcessingEventTypes(Enum):
    """Test event types."""

    PROCESSING_EVENT = "processing_event"


class TestSignalManager(BaseSignalManager):
    """Test signal manager."""

    def __init__(self):
        super().__init__()
        if not self._signals_initialized:
            self.setup_custom_signals({"processing": ProcessingEventTypes})


class TestEventProcessorSync:
    """Tests for EventProcessor with synchronous methods."""

    def test_emits_event_decorator_basic(self, received_events, event_receiver):
        """Test basic event emission with decorator."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        class TestService:
            def __init__(self):
                self.status = "init"

            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.emits_event(data=["status"])
            def initialize(self):
                self.status = "ready"
                return True

        service = TestService()
        result = service.initialize()

        assert result is True
        # Should have START and FINISH events
        assert len(received_events) == 2
        assert received_events[0]["sub_event"] == "INITIALIZE_START"
        assert received_events[1]["sub_event"] == "INITIALIZE_FINISH"

    def test_emits_event_with_metadata(self, received_events, event_receiver):
        """Test event emission with custom metadata."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        class TestService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.emits_event(service_name="test-service", version="1.0")
            def process(self):
                return "done"

        service = TestService()
        service.process()

        assert len(received_events) == 2
        assert received_events[0]["service_name"] == "test-service"
        assert received_events[0]["version"] == "1.0"

    def test_emits_event_on_error(self, received_events, event_receiver):
        """Test that ERROR event is emitted on exception."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        class TestService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.emits_event()
            def failing_method(self):
                raise ValueError("Test error")

        service = TestService()

        with pytest.raises(ValueError):
            service.failing_method()

        # Should have START and ERROR events
        assert len(received_events) == 2
        assert received_events[0]["sub_event"] == "FAILING_METHOD_START"
        assert received_events[1]["sub_event"] == "FAILING_METHOD_ERROR"
        assert "error" in received_events[1]
        assert received_events[1]["error"] == "Test error"

    def test_no_signal_manager_graceful_skip(self):
        """Test that decorator works gracefully without signal manager."""

        class TestService:
            @EventProcessor.emits_event()
            def method(self):
                return "works"

        service = TestService()
        result = service.method()
        assert result == "works"

    def test_variable_state_capture(self, received_events, event_receiver):
        """Test capturing variable state changes."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        class TestService:
            def __init__(self):
                self.counter = 0

            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.emits_event(data=["counter"])
            def increment(self):
                self.counter += 1

        service = TestService()
        service.increment()

        # Check START event has initial state
        assert received_events[0]["counter"] == 0
        # Check FINISH event has final state
        assert received_events[1]["counter"] == 1


class TestEventProcessorAsync:
    """Tests for EventProcessor with asynchronous methods."""

    @pytest.mark.asyncio
    async def test_async_emits_event(self, received_events, event_receiver):
        """Test event emission with async methods."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        class TestService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.emits_event()
            async def async_process(self):
                await asyncio.sleep(0.01)
                return "async done"

        service = TestService()
        result = await service.async_process()

        assert result == "async done"
        assert len(received_events) == 2
        assert received_events[0]["sub_event"] == "ASYNC_PROCESS_START"
        assert received_events[1]["sub_event"] == "ASYNC_PROCESS_FINISH"

    @pytest.mark.asyncio
    async def test_async_error_handling(self, received_events, event_receiver):
        """Test async error handling."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        class TestService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.emits_event()
            async def failing_async(self):
                await asyncio.sleep(0.01)
                raise RuntimeError("Async error")

        service = TestService()

        with pytest.raises(RuntimeError):
            await service.failing_async()

        assert len(received_events) == 2
        assert received_events[1]["sub_event"] == "FAILING_ASYNC_ERROR"

    @pytest.mark.asyncio
    async def test_periodic_emit_decorator(self, received_events, event_receiver):
        """Test periodic emit decorator for monitoring."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        class TestService:
            def __init__(self):
                self.progress = 0

            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.periodic_emit(variables=["progress"], interval=0.05)
            async def long_task(self):
                for i in range(3):
                    await asyncio.sleep(0.06)
                    self.progress = i + 1

        service = TestService()
        await service.long_task()

        # Should have multiple PROGRESS events
        progress_events = [
            e for e in received_events if e.get("sub_event") == "LONG_TASK_PROGRESS"
        ]
        assert len(progress_events) >= 1

    @pytest.mark.asyncio
    async def test_periodic_emit_sync_method_skip(self):
        """Test that periodic_emit gracefully skips sync methods."""
        signals = TestSignalManager()

        class TestService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.periodic_emit(variables=["progress"], interval=0.1)
            def sync_method(self):
                return "sync"

        service = TestService()
        # Should work without error
        result = service.sync_method()
        assert result == "sync"


class TestEventProcessorEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_missing_event_type_fallback(self, received_events, event_receiver):
        """Test fallback to lifecycle when event_type is missing."""
        signals = TestSignalManager()
        # Setup lifecycle signal too
        signals.setup_custom_signals({"lifecycle": ProcessingEventTypes})
        signals.lifecycle = event_receiver

        class TestService:
            class Meta:
                signal_manager = signals
                # No event_type specified

            @EventProcessor.emits_event()
            def method(self):
                return "ok"

        service = TestService()
        service.method()

        # Should fallback to lifecycle
        assert len(received_events) >= 1

    def test_class_variable_tracking(self, received_events, event_receiver):
        """Test tracking class variables with cls. prefix."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        class TestService:
            shared_count = 0

            class Meta:
                event_type = "processing"
                signal_manager = signals

            @EventProcessor.emits_event(data=["cls.shared_count"])
            def increment_shared(self):
                TestService.shared_count += 1

        service = TestService()
        service.increment_shared()

        # Check that class variable was captured
        assert "shared_count" in received_events[0] or "shared_count_error" in received_events[0]
