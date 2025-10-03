"""Basic signal manager example.

This example demonstrates:
- Creating a custom signal manager
- Setting up signals with enums
- Connecting receivers to signals
- Emitting events
"""

from champi_signals import BaseSignalManager, STTEventTypes


class STTSignalManager(BaseSignalManager):
    """Custom STT Signal Manager."""

    def __init__(self):
        super().__init__()
        if not self._signals_initialized:
            # Setup signals using predefined enums
            self.setup_custom_signals(
                {
                    "lifecycle": STTEventTypes,
                    "model": STTEventTypes,
                    "processing": STTEventTypes,
                    "telemetry": STTEventTypes,
                }
            )


def main():
    """Run the basic example."""
    # Create signal manager (singleton)
    signals = STTSignalManager()

    # Connect receiver to processing signal
    def handle_processing_events(_sender, **kwargs):
        event_type = kwargs.get("event_type")
        sub_event = kwargs.get("sub_event")
        data = kwargs.get("data", {})
        print(f"[{event_type}] {sub_event}: {data}")

    # Connect using property setter
    signals.processing = handle_processing_events

    # Emit some events
    print("Emitting transcription start event...")
    signals.processing.send(
        event_type="processing",
        sub_event="TRANSCRIPTION_START",
        data={"audio_duration": 5.2, "language": "en"},
    )

    print("\nEmitting transcription complete event...")
    signals.processing.send(
        event_type="processing",
        sub_event="TRANSCRIPTION_COMPLETE",
        data={"text": "Hello world", "confidence": 0.95},
    )

    # You can connect multiple receivers
    def handle_processing_for_logging(_sender, **kwargs):
        print(f"[LOGGER] Event received: {kwargs.get('sub_event')}")

    signals.processing = handle_processing_for_logging

    print("\nEmitting with multiple receivers...")
    signals.processing.send(
        event_type="processing",
        sub_event="TRANSCRIPTION_ERROR",
        data={"error": "timeout"},
    )


if __name__ == "__main__":
    main()
