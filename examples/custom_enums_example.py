"""Custom enum setup example.

This example demonstrates:
- Creating custom service enums using EnumSetup
- Using custom enums with signal managers
- Setting up service-specific event types
"""

from champi_signals import BaseSignalManager, EnumSetup, EventProcessor


def main():
    """Run the custom enums example."""
    print("=== Creating Custom NLP Service Enums ===\n")

    # Create custom enums for an NLP service
    nlp_enums = EnumSetup.setup_service_enums(
        "NLP",
        {
            "event_types": ["lifecycle", "processing", "analysis"],
            "lifecycle": ["idle", "loading", "ready", "analyzing", "complete"],
            "processing": ["tokenize", "parse", "extract", "classify"],
        },
    )

    # Inspect created enums
    print("Created Enums:")
    for enum_name, enum_class in nlp_enums.items():
        print(f"\n{enum_name}:")
        for member in enum_class:
            print(f"  {member.name} = {member.value}")

    # Create signal manager with custom enums
    print("\n\n=== Creating NLP Signal Manager ===\n")

    class NLPSignalManager(BaseSignalManager):
        """NLP-specific signal manager."""

        def __init__(self):
            super().__init__()
            if not self._signals_initialized:
                self.setup_custom_signals(
                    {
                        "lifecycle": nlp_enums["EventTypes"],
                        "processing": nlp_enums["EventTypes"],
                        "analysis": nlp_enums["EventTypes"],
                    }
                )

    # Create and use the signal manager
    signals = NLPSignalManager()

    def nlp_event_handler(_sender, **kwargs):
        event_type = kwargs.get("event_type")
        sub_event = kwargs.get("sub_event")
        data = kwargs.get("data", {})
        print(f"[{event_type}] {sub_event}: {data}")

    # Connect receivers
    signals.processing = nlp_event_handler
    signals.analysis = nlp_event_handler

    # Emit events
    print("Emitting NLP events:\n")

    signals.processing.send(
        event_type="processing",
        sub_event="TOKENIZE_START",
        data={"text": "Hello world", "language": "en"},
    )

    signals.processing.send(
        event_type="processing",
        sub_event="PARSE_COMPLETE",
        data={"tokens": 2, "duration_ms": 5},
    )

    signals.analysis.send(
        event_type="analysis",
        sub_event="CLASSIFY_RESULT",
        data={"category": "greeting", "confidence": 0.95},
    )

    # Create an NLP service using the custom enums
    print("\n\n=== Creating NLP Service with EventProcessor ===\n")

    class NLPService:
        """Example NLP service."""

        def __init__(self):
            self.tokens = []
            self.classifications = []

        class Meta:
            event_type = "processing"
            signal_manager = NLPSignalManager()

        @EventProcessor.emits_event(data=["tokens"])
        def tokenize(self, text: str):
            """Tokenize text."""
            self.tokens = text.split()
            print(f"Tokenized: {self.tokens}")
            return self.tokens

        @EventProcessor.emits_event(data=["classifications"])
        def classify(self, tokens: list):
            """Classify tokens."""
            classification = (
                "greeting" if "hello" in [t.lower() for t in tokens] else "other"
            )
            self.classifications.append(classification)
            print(f"Classification: {classification}")
            return classification

    # Use the service
    service = NLPService()
    tokens = service.tokenize("Hello world")
    classification = service.classify(tokens)

    print(f"\nFinal result: {tokens} -> {classification}")


if __name__ == "__main__":
    main()
