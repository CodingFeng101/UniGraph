from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Identified:
    """A protocol for an item with an ID."""

    id: str
    """The ID of the item."""
