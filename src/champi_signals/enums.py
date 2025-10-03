"""Enums extracted from Champi services with setup methods."""

from enum import Enum, unique


@unique
class STTEventTypes(Enum):
    """Main event type categories for STT service"""

    LIFECYCLE_EVENT = "lifecycle_event"
    MODEL_EVENT = "model_event"
    PROCESSING_EVENT = "processing_event"
    TELEMETRY_EVENT = "telemetry_event"


@unique
class TTSEventTypes(Enum):
    """Main event type categories for TTS service"""

    LIFECYCLE_EVENT = "lifecycle_event"
    MODEL_EVENT = "model_event"
    PROCESSING_EVENT = "processing_event"
    TELEMETRY_EVENT = "telemetry_event"


class EnumSetup:
    """Utility class for setting up custom service enums."""

    @staticmethod
    def create_event_types(
        service_name: str, event_categories: list[str] = None
    ) -> type[Enum]:
        """
        Create a custom EventTypes enum for a service.

        Args:
            service_name: Name of the service (e.g., 'NLP', 'AUDIO')
            event_categories: List of event categories. Defaults to standard categories.

        Returns:
            Enum class with event types

        Example:
            NLPEventTypes = EnumSetup.create_event_types(
                'NLP', ['lifecycle', 'processing', 'analysis']
            )
        """
        if event_categories is None:
            event_categories = ["lifecycle", "model", "processing", "telemetry"]

        # Create enum attributes
        enum_attrs = {}
        for category in event_categories:
            enum_name = f"{category.upper()}_EVENT"
            enum_value = f"{category.lower()}_event"
            enum_attrs[enum_name] = enum_value

        # Create the enum class dynamically
        return Enum(f"{service_name}EventTypes", enum_attrs)

    @staticmethod
    def create_lifecycle_events(
        service_name: str, custom_events: list[str] = None
    ) -> type[Enum]:
        """
        Create a custom LifecycleEvents enum for a service.

        Args:
            service_name: Name of the service
        custom_events: Custom lifecycle events. If None, uses standard events.

        Returns:
            Enum class with lifecycle events
        """
        if custom_events is None:
            custom_events = [
                "uninitialized",
                "initializing",
                "ready",
                "processing",
                "error",
                "shutdown",
                "stopped",
                "standby",
            ]

        enum_attrs = {event.upper(): event.lower() for event in custom_events}
        return Enum(f"{service_name}LifecycleEvents", enum_attrs)

    @staticmethod
    def create_processing_events(
        service_name: str, custom_events: list[str]
    ) -> type[Enum]:
        """
        Create a custom ProcessingEvents enum for a service.

        Args:
            service_name: Name of the service
            custom_events: List of processing event names

        Returns:
            Enum class with processing events
        """
        enum_attrs = {event.upper(): event.lower() for event in custom_events}
        return Enum(f"{service_name}ProcessingEvents", enum_attrs)

    @staticmethod
    def setup_service_enums(
        service_name: str, config: dict[str, list[str]]
    ) -> dict[str, type[Enum]]:
        """
        Setup all enums for a service at once.

        Args:
            service_name: Name of the service
            config: Dictionary with enum types and their events

        Returns:
            Dictionary mapping enum type names to enum classes

        Example:
            enums = EnumSetup.setup_service_enums('NLP', {
                'event_types': ['lifecycle', 'processing', 'analysis'],
                'lifecycle': ['idle', 'analyzing', 'complete'],
                'processing': ['tokenize', 'parse', 'classify']
            })
        """
        result = {}

        if "event_types" in config:
            result["EventTypes"] = EnumSetup.create_event_types(
                service_name, config["event_types"]
            )

        if "lifecycle" in config:
            result["LifecycleEvents"] = EnumSetup.create_lifecycle_events(
                service_name, config["lifecycle"]
            )

        if "processing" in config:
            result["ProcessingEvents"] = EnumSetup.create_processing_events(
                service_name, config["processing"]
            )

        # Handle any other custom enum types
        for enum_type, events in config.items():
            if enum_type not in ["event_types", "lifecycle", "processing"]:
                enum_name = f"{enum_type.title()}Events"
                enum_attrs = {event.upper(): event.lower() for event in events}
                result[enum_name] = Enum(f"{service_name}{enum_name}", enum_attrs)

        return result
