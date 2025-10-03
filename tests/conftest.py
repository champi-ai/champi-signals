"""Pytest configuration and fixtures for champi_signals tests."""

import pytest
from enum import Enum


@pytest.fixture
def sample_enum():
    """Sample enum for testing."""

    class SampleEventTypes(Enum):
        LIFECYCLE_EVENT = "lifecycle_event"
        PROCESSING_EVENT = "processing_event"

    return SampleEventTypes


@pytest.fixture
def signal_config(sample_enum):
    """Sample signal configuration."""
    return {"lifecycle": sample_enum, "processing": sample_enum}


@pytest.fixture
def received_events():
    """List to collect received events."""
    return []


@pytest.fixture
def event_receiver(received_events):
    """Event receiver function for testing."""

    def receiver(sender, **kwargs):
        received_events.append({"sender": sender, **kwargs})

    return receiver
