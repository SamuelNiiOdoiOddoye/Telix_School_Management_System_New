"""Identifier generation."""

from uuid import uuid4


def generate_id(prefix: str) -> str:
    """Create an ID such as ``STU-1A2B3C4D``."""
    return f"{prefix}-{uuid4().hex[:8].upper()}"
