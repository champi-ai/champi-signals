"""Tests that verify all public symbols are correctly exported from the package."""

import champi_signals


def test_base_signal_manager_exported():
    """BaseSignalManager is exported from the top-level package."""
    assert champi_signals.BaseSignalManager is not None


def test_event_processor_exported():
    """EventProcessor is exported from the top-level package."""
    assert champi_signals.EventProcessor is not None


def test_stt_event_types_exported():
    """STTEventTypes is exported from the top-level package."""
    assert champi_signals.STTEventTypes is not None


def test_tts_event_types_exported():
    """TTSEventTypes is exported from the top-level package."""
    assert champi_signals.TTSEventTypes is not None


def test_enum_setup_exported():
    """EnumSetup is exported from the top-level package."""
    assert champi_signals.EnumSetup is not None


def test_signal_bridge_abc_exported():
    """SignalBridgeABC is exported from the top-level package."""
    assert champi_signals.SignalBridgeABC is not None


def test_all_symbols_in_dunder_all():
    """All required v0.2.0 symbols are listed in __all__."""
    required = {
        "BaseSignalManager",
        "EventProcessor",
        "STTEventTypes",
        "TTSEventTypes",
        "EnumSetup",
        "SignalBridgeABC",
    }
    assert required.issubset(set(champi_signals.__all__))
