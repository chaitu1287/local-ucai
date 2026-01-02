"""Database enums for AIUC evaluation system."""

from enum import Enum


class Platform(str, Enum):
    """Supported platforms for products."""

    # TODO: Add more platforms here
    TEST = "Test"
    INTERCOM = "Intercom"
    ADA = "Ada"
    POINTER = "Pointer"
    RECRAFT = "Recraft"
    ELEVENLABS = "ElevenLabs"


class BatchStatus(str, Enum):
    """Status values for evaluation batches."""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class EvalStatus(str, Enum):
    """Status values for individual evaluations."""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    GRADED = "Graded"
    FAILED = "Failed"


class Severity(str, Enum):
    """Severity levels for grading."""

    PASS = "Pass"
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
