"""Async event processing example.

This example demonstrates:
- Using EventProcessor with async methods
- Periodic variable monitoring during async execution
- Async error handling with events
"""

import asyncio

from champi_signals import BaseSignalManager, EventProcessor, STTEventTypes


class STTSignalManager(BaseSignalManager):
    """STT Signal Manager."""

    def __init__(self):
        super().__init__()
        if not self._signals_initialized:
            self.setup_custom_signals(
                {
                    "lifecycle": STTEventTypes,
                    "processing": STTEventTypes,
                }
            )


class AsyncSTTService:
    """Example async STT service."""

    def __init__(self):
        self.status = "idle"
        self.progress = 0
        self.transcriptions = []

    class Meta:
        event_type = "processing"
        signal_manager = STTSignalManager()

    @EventProcessor.emits_event(data=["status"])
    async def initialize(self):
        """Async initialization."""
        print("Initializing async STT service...")
        await asyncio.sleep(0.5)
        self.status = "ready"
        print("Initialization complete!")

    @EventProcessor.emits_event(data=["transcriptions"])
    async def transcribe(self, audio_file: str):
        """Async transcription."""
        print(f"Transcribing {audio_file}...")
        await asyncio.sleep(1)
        transcription = f"Transcribed content of {audio_file}"
        self.transcriptions.append(transcription)
        print(f"Transcription complete: {transcription}")
        return transcription

    @EventProcessor.periodic_emit(variables=["progress"], interval=0.3)
    async def long_transcription(self, audio_file: str, duration: float):
        """Long transcription with progress monitoring."""
        print(f"Starting long transcription of {audio_file} ({duration}s)...")

        steps = 5
        for i in range(steps):
            await asyncio.sleep(duration / steps)
            self.progress = int((i + 1) / steps * 100)
            print(f"Progress: {self.progress}%")

        self.transcriptions.append(f"Long transcription of {audio_file}")
        self.progress = 0
        return "Complete"

    @EventProcessor.emits_event(data=["status"])
    async def failing_transcription(self):
        """Async method that fails."""
        print("Starting transcription that will fail...")
        await asyncio.sleep(0.3)
        raise RuntimeError("Transcription failed: audio corrupted")


async def main():
    """Run the async example."""
    # Setup signal manager and receivers
    signals = STTSignalManager()

    def event_logger(_sender, **kwargs):
        event = kwargs.get("sub_event", "UNKNOWN")
        event_type = kwargs.get("event_type", "")
        data = kwargs.get("data", {})

        if "PROGRESS" in event:
            # Special formatting for progress events
            progress = data.get("progress", 0)
            print(f"  [PROGRESS] {progress}%")
        else:
            print(f"\n[EVENT: {event_type}] {event}")
            for key, value in data.items():
                if not key.startswith("_") and key != "timestamp":
                    print(f"  {key}: {value}")

    signals.processing = event_logger

    # Create service
    print("=== Creating Async STT Service ===")
    service = AsyncSTTService()

    # Initialize
    print("\n=== Initialization ===")
    await service.initialize()

    # Simple transcription
    print("\n=== Simple Transcription ===")
    result = await service.transcribe("audio1.wav")
    print(f"Result: {result}")

    # Long transcription with progress monitoring
    print("\n=== Long Transcription with Progress Monitoring ===")
    result = await service.long_transcription("long_audio.wav", duration=2.0)
    print(f"Result: {result}")

    # Error handling
    print("\n=== Testing Async Error Handling ===")
    try:
        await service.failing_transcription()
    except RuntimeError as e:
        print(f"Caught expected error: {e}")

    # Concurrent transcriptions
    print("\n=== Concurrent Transcriptions ===")
    results = await asyncio.gather(
        service.transcribe("audio2.wav"),
        service.transcribe("audio3.wav"),
        service.transcribe("audio4.wav"),
    )
    print(f"Concurrent results: {results}")

    print(f"\nTotal transcriptions: {len(service.transcriptions)}")


if __name__ == "__main__":
    asyncio.run(main())
