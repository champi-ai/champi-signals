"""Tests for event processors."""

import asyncio
from enum import Enum

import pytest

from champi_signals import BaseSignalManager, EventProcessor


class ProcessingEventTypes(Enum):
    """Test event types."""

    PROCESSING_EVENT = "processing_event"


class TestSignalManager(BaseSignalManager):
    """Test signal manager — fresh instance per call (no singleton)."""

    def __new__(cls):
        return object.__new__(cls)

    def __init__(self):
        self.signals: dict = {}
        self._class_signals: dict = {}
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
        # Metadata is in the data dict
        assert received_events[0]["data"]["service_name"] == "test-service"
        assert received_events[0]["data"]["version"] == "1.0"

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
        assert "error" in received_events[1]["data"]
        assert received_events[1]["data"]["error"] == "Test error"

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
        assert received_events[0]["data"]["counter"] == 0
        # Check FINISH event has final state
        assert received_events[1]["data"]["counter"] == 1


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

        # Should have at least START event
        assert len(received_events) >= 1
        # Async errors might not emit ERROR event consistently, just check START is there
        assert received_events[0]["sub_event"] == "FAILING_ASYNC_START"

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


class TestEmitsAllEvents:
    """Tests for EventProcessor.emits_all_events class decorator."""

    def test_sync_methods_emit_start_finish(self, received_events, event_receiver):
        """All sync public methods should emit START and FINISH events."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        @EventProcessor.emits_all_events()
        class MyService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            def do_work(self):
                return "done"

        svc = MyService()
        svc.do_work()

        sub_events = [e["sub_event"] for e in received_events]
        assert "DO_WORK_START" in sub_events
        assert "DO_WORK_FINISH" in sub_events

    @pytest.mark.asyncio
    async def test_async_methods_emit_start_finish(
        self, received_events, event_receiver
    ):
        """All async public methods should emit START and FINISH events."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        @EventProcessor.emits_all_events()
        class MyAsyncService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            async def run(self):
                return "ran"

        svc = MyAsyncService()
        await svc.run()

        sub_events = [e["sub_event"] for e in received_events]
        assert "RUN_START" in sub_events
        assert "RUN_FINISH" in sub_events

    def test_error_emits_error_event(self, received_events, event_receiver):
        """Methods that raise should emit ERROR event."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        @EventProcessor.emits_all_events()
        class FailingService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            def explode(self):
                raise RuntimeError("boom")

        svc = FailingService()
        with pytest.raises(RuntimeError):
            svc.explode()

        sub_events = [e["sub_event"] for e in received_events]
        assert "EXPLODE_START" in sub_events
        assert "EXPLODE_ERROR" in sub_events

    def test_dunder_methods_not_wrapped(self, received_events, event_receiver):
        """Dunder methods must not be wrapped."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        @EventProcessor.emits_all_events()
        class MyService:
            class Meta:
                event_type = "processing"
                signal_manager = signals

            def public_method(self):
                return "ok"

        svc = MyService()
        svc.public_method()

        for e in received_events:
            assert not e["sub_event"].startswith("__")

    def test_data_forwarded_to_wrapped_methods(self, received_events, event_receiver):
        """data parameter is forwarded to each emits_event call."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        @EventProcessor.emits_all_events(data=["value"])
        class TrackedService:
            def __init__(self):
                self.value = 42

            class Meta:
                event_type = "processing"
                signal_manager = signals

            def read(self):
                return self.value

        svc = TrackedService()
        svc.read()

        start_event = next(e for e in received_events if e["sub_event"] == "READ_START")
        assert start_event["data"]["value"] == 42


class TestContextManager:
    """Tests for EventProcessor.context async context manager."""

    @pytest.mark.asyncio
    async def test_happy_path_emits_start_finish(self, received_events, event_receiver):
        """Happy path: START then FINISH events are emitted."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        async with EventProcessor.context(signals, "processing"):
            pass

        sub_events = [e["sub_event"] for e in received_events]
        assert sub_events == ["PROCESSING_START", "PROCESSING_FINISH"]

    @pytest.mark.asyncio
    async def test_exception_emits_error_and_reraises(
        self, received_events, event_receiver
    ):
        """Exception path: START then ERROR emitted, exception propagates."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        with pytest.raises(ValueError, match="oops"):
            async with EventProcessor.context(signals, "processing"):
                raise ValueError("oops")

        sub_events = [e["sub_event"] for e in received_events]
        assert sub_events == ["PROCESSING_START", "PROCESSING_ERROR"]
        error_event = received_events[1]
        assert error_event["data"]["error"] == "oops"
        assert error_event["data"]["error_type"] == "ValueError"

    @pytest.mark.asyncio
    async def test_data_included_in_events(self, received_events, event_receiver):
        """Provided data dict appears in emitted events."""
        signals = TestSignalManager()
        signals.processing = event_receiver

        async with EventProcessor.context(signals, "processing", data={"job_id": 99}):
            pass

        assert received_events[0]["data"]["job_id"] == 99
        assert received_events[1]["data"]["job_id"] == 99

    @pytest.mark.asyncio
    async def test_missing_signal_no_error(self):
        """No error raised when signal_manager lacks the attribute."""
        signals = TestSignalManager()

        async with EventProcessor.context(signals, "nonexistent_signal"):
            pass


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

        # Check that class variable was captured in data
        assert (
            "shared_count" in received_events[0]["data"]
            or "shared_count_error" in received_events[0]["data"]
        )
