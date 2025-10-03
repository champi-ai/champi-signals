"""EventProcessor decorator example.

This example demonstrates:
- Using EventProcessor with metaclass signal manager extraction
- Automatic START/FINISH/ERROR event emission
- State variable tracking
- Custom metadata in events
"""

from champi_signals import BaseSignalManager, EventProcessor, TTSEventTypes


class TTSSignalManager(BaseSignalManager):
    """Custom TTS Signal Manager."""

    def __init__(self):
        super().__init__()
        if not self._signals_initialized:
            self.setup_custom_signals(
                {
                    "lifecycle": TTSEventTypes,
                    "processing": TTSEventTypes,
                }
            )


class TTSService:
    """Example TTS service with event processing."""

    def __init__(self):
        self.status = "uninitialized"
        self.synthesis_count = 0
        self.last_text = ""

    class Meta:
        """Metaclass configuration for EventProcessor."""

        event_type = "processing"
        signal_manager = TTSSignalManager()

    @EventProcessor.emits_event(
        data=["status", "synthesis_count"], service="tts", version="1.0"
    )
    def initialize(self):
        """Initialize the TTS service.

        This will automatically emit:
        - INITIALIZE_START (with initial state)
        - INITIALIZE_FINISH (with final state)
        - INITIALIZE_ERROR (if exception occurs)
        """
        print("Initializing TTS service...")
        self.status = "ready"
        return True

    @EventProcessor.emits_event(data=["synthesis_count", "last_text"])
    def synthesize(self, text: str):
        """Synthesize speech from text."""
        print(f"Synthesizing: {text}")
        self.last_text = text
        self.synthesis_count += 1

        # Simulate some processing
        audio_duration = len(text) * 0.1
        return {"audio_duration": audio_duration, "format": "wav"}

    @EventProcessor.emits_event(data=["status"])
    def shutdown(self):
        """Shutdown the service."""
        print("Shutting down...")
        self.status = "stopped"


def main():
    """Run the event processor example."""
    # Get signal manager and connect receivers
    signals = TTSSignalManager()

    def event_logger(sender, **kwargs):
        event = kwargs.get("sub_event", "UNKNOWN")
        data = kwargs.get("data", {})
        print(f"\n[EVENT] {event}")
        for key, value in data.items():
            if not key.startswith("_"):
                print(f"  {key}: {value}")

    signals.processing = event_logger

    # Create service and use it
    print("=== Creating TTS Service ===")
    service = TTSService()

    print("\n=== Initializing Service ===")
    service.initialize()

    print("\n=== Synthesizing Speech ===")
    result1 = service.synthesize("Hello world")
    print(f"Result: {result1}")

    print("\n=== Synthesizing Again ===")
    result2 = service.synthesize("How are you?")
    print(f"Result: {result2}")

    print("\n=== Shutting Down ===")
    service.shutdown()

    print("\n=== Testing Error Handling ===")

    @EventProcessor.emits_event(data=["status"])
    def failing_method(self):
        raise ValueError("Simulated error")

    # Temporarily add method to service
    TTSService.failing_method = failing_method

    try:
        service.failing_method()
    except ValueError as e:
        print(f"Caught expected error: {e}")


if __name__ == "__main__":
    main()
