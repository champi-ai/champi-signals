"""Tests for enum utilities."""

import pytest
from enum import Enum
from champi_signals import STTEventTypes, TTSEventTypes, EnumSetup


class TestPreDefinedEnums:
    """Tests for pre-defined event type enums."""

    def test_stt_event_types(self):
        """Test STTEventTypes enum."""
        assert hasattr(STTEventTypes, "LIFECYCLE_EVENT")
        assert hasattr(STTEventTypes, "MODEL_EVENT")
        assert hasattr(STTEventTypes, "PROCESSING_EVENT")
        assert hasattr(STTEventTypes, "TELEMETRY_EVENT")

        assert STTEventTypes.LIFECYCLE_EVENT.value == "lifecycle_event"
        assert STTEventTypes.MODEL_EVENT.value == "model_event"
        assert STTEventTypes.PROCESSING_EVENT.value == "processing_event"
        assert STTEventTypes.TELEMETRY_EVENT.value == "telemetry_event"

    def test_tts_event_types(self):
        """Test TTSEventTypes enum."""
        assert hasattr(TTSEventTypes, "LIFECYCLE_EVENT")
        assert hasattr(TTSEventTypes, "MODEL_EVENT")
        assert hasattr(TTSEventTypes, "PROCESSING_EVENT")
        assert hasattr(TTSEventTypes, "TELEMETRY_EVENT")

        assert TTSEventTypes.LIFECYCLE_EVENT.value == "lifecycle_event"

    def test_enum_values_are_unique(self):
        """Test that enum values are unique."""
        stt_values = [e.value for e in STTEventTypes]
        assert len(stt_values) == len(set(stt_values))

        tts_values = [e.value for e in TTSEventTypes]
        assert len(tts_values) == len(set(tts_values))


class TestEnumSetup:
    """Tests for EnumSetup utility class."""

    def test_create_event_types_default(self):
        """Test creating event types with default categories."""
        NLPEventTypes = EnumSetup.create_event_types("NLP")

        assert hasattr(NLPEventTypes, "LIFECYCLE_EVENT")
        assert hasattr(NLPEventTypes, "MODEL_EVENT")
        assert hasattr(NLPEventTypes, "PROCESSING_EVENT")
        assert hasattr(NLPEventTypes, "TELEMETRY_EVENT")

        assert NLPEventTypes.LIFECYCLE_EVENT.value == "lifecycle_event"

    def test_create_event_types_custom(self):
        """Test creating event types with custom categories."""
        CustomEventTypes = EnumSetup.create_event_types(
            "Custom", ["lifecycle", "processing", "analysis"]
        )

        assert hasattr(CustomEventTypes, "LIFECYCLE_EVENT")
        assert hasattr(CustomEventTypes, "PROCESSING_EVENT")
        assert hasattr(CustomEventTypes, "ANALYSIS_EVENT")
        assert not hasattr(CustomEventTypes, "MODEL_EVENT")

        assert CustomEventTypes.ANALYSIS_EVENT.value == "analysis_event"

    def test_create_lifecycle_events_default(self):
        """Test creating lifecycle events with defaults."""
        NLPLifecycle = EnumSetup.create_lifecycle_events("NLP")

        assert hasattr(NLPLifecycle, "UNINITIALIZED")
        assert hasattr(NLPLifecycle, "INITIALIZING")
        assert hasattr(NLPLifecycle, "READY")
        assert hasattr(NLPLifecycle, "PROCESSING")
        assert hasattr(NLPLifecycle, "ERROR")
        assert hasattr(NLPLifecycle, "SHUTDOWN")

        assert NLPLifecycle.READY.value == "ready"

    def test_create_lifecycle_events_custom(self):
        """Test creating lifecycle events with custom events."""
        CustomLifecycle = EnumSetup.create_lifecycle_events(
            "Custom", ["idle", "active", "paused"]
        )

        assert hasattr(CustomLifecycle, "IDLE")
        assert hasattr(CustomLifecycle, "ACTIVE")
        assert hasattr(CustomLifecycle, "PAUSED")

        assert CustomLifecycle.IDLE.value == "idle"

    def test_create_processing_events(self):
        """Test creating processing events."""
        NLPProcessing = EnumSetup.create_processing_events(
            "NLP", ["tokenize", "parse", "classify"]
        )

        assert hasattr(NLPProcessing, "TOKENIZE")
        assert hasattr(NLPProcessing, "PARSE")
        assert hasattr(NLPProcessing, "CLASSIFY")

        assert NLPProcessing.TOKENIZE.value == "tokenize"

    def test_setup_service_enums_comprehensive(self):
        """Test setting up complete service enums."""
        enums = EnumSetup.setup_service_enums(
            "NLP",
            {
                "event_types": ["lifecycle", "processing", "analysis"],
                "lifecycle": ["idle", "analyzing", "complete"],
                "processing": ["tokenize", "parse", "extract"],
            },
        )

        assert "EventTypes" in enums
        assert "LifecycleEvents" in enums
        assert "ProcessingEvents" in enums

        # Test EventTypes
        assert hasattr(enums["EventTypes"], "LIFECYCLE_EVENT")
        assert hasattr(enums["EventTypes"], "ANALYSIS_EVENT")

        # Test LifecycleEvents
        assert hasattr(enums["LifecycleEvents"], "IDLE")
        assert hasattr(enums["LifecycleEvents"], "ANALYZING")

        # Test ProcessingEvents
        assert hasattr(enums["ProcessingEvents"], "TOKENIZE")
        assert hasattr(enums["ProcessingEvents"], "PARSE")

    def test_setup_service_enums_custom_categories(self):
        """Test setting up service enums with custom categories."""
        enums = EnumSetup.setup_service_enums(
            "Audio",
            {
                "event_types": ["lifecycle", "audio"],
                "audio": ["record", "playback", "process"],
            },
        )

        assert "EventTypes" in enums
        assert "AudioEvents" in enums

        assert hasattr(enums["AudioEvents"], "RECORD")
        assert hasattr(enums["AudioEvents"], "PLAYBACK")
        assert enums["AudioEvents"].RECORD.value == "record"

    def test_setup_service_enums_partial(self):
        """Test setting up service enums with only some categories."""
        enums = EnumSetup.setup_service_enums(
            "Simple", {"event_types": ["lifecycle", "processing"]}
        )

        assert "EventTypes" in enums
        assert "LifecycleEvents" not in enums
        assert "ProcessingEvents" not in enums

    def test_enum_name_formatting(self):
        """Test that enum names are properly formatted."""
        enums = EnumSetup.setup_service_enums(
            "TestService", {"custom_type": ["event1", "event2"]}
        )

        # Should have Custom_TypeEvents (matches implementation)
        assert "Custom_TypeEvents" in enums
        assert hasattr(enums["Custom_TypeEvents"], "EVENT1")

    def test_all_enums_are_proper_enums(self):
        """Test that all created types are proper Enum classes."""
        enums = EnumSetup.setup_service_enums(
            "Test",
            {
                "event_types": ["lifecycle"],
                "lifecycle": ["ready"],
                "processing": ["process"],
            },
        )

        for enum_type in enums.values():
            assert issubclass(enum_type, Enum)


class TestEnumIntegration:
    """Integration tests for enums with signal managers."""

    def test_enums_with_signal_manager(self):
        """Test using custom enums with signal manager."""
        from champi_signals import BaseSignalManager

        # Create custom enums
        enums = EnumSetup.setup_service_enums(
            "NLP", {"event_types": ["lifecycle", "processing"]}
        )

        # Create unique signal manager class
        class NLPSignalManager(BaseSignalManager):
            _instance = None
            _signals_initialized = False

            def __init__(self):
                if type(self)._instance is None:
                    type(self)._instance = self
                if not type(self)._signals_initialized:
                    self.signals = {}
                    self._class_signals = {}
                    self.setup_custom_signals(
                        {
                            "lifecycle": enums["EventTypes"],
                            "processing": enums["EventTypes"],
                        }
                    )
                    type(self)._signals_initialized = True

        manager = NLPSignalManager()
        assert hasattr(manager, "lifecycle")
        assert hasattr(manager, "processing")

    def test_predefined_enums_with_signal_manager(self):
        """Test using pre-defined enums with signal manager."""
        from champi_signals import BaseSignalManager

        # Create unique signal manager class
        class STTSignalManager3(BaseSignalManager):
            _instance = None
            _signals_initialized = False

            def __init__(self):
                if type(self)._instance is None:
                    type(self)._instance = self
                if not type(self)._signals_initialized:
                    self.signals = {}
                    self._class_signals = {}
                    self.setup_custom_signals(
                        {
                            "lifecycle": STTEventTypes,
                            "model": STTEventTypes,
                            "processing": STTEventTypes,
                            "telemetry": STTEventTypes,
                        }
                    )
                    type(self)._signals_initialized = True

        manager = STTSignalManager3()
        assert hasattr(manager, "lifecycle")
        assert hasattr(manager, "model")
        assert hasattr(manager, "processing")
        assert hasattr(manager, "telemetry")
