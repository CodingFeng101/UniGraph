from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .identified import Identified


@dataclass
class Community(Identified):
    """A protocol for a community in the system."""

    title: str = ''
    """Title of the community."""

    level: str = ''
    """Community level."""

    full_content: str = ''
    """Full content of the report."""

    entity_ids: list[str] | None = None
    """List of entity IDs related to the community (optional)."""

    rating: float | None = None
    """Community rating."""

    attributes: dict[str, Any] | None = None
    """A dictionary of additional attributes associated with the community (optional). To be included in the search 
    prompt."""

    @classmethod
    def from_dict(
        cls,
        d: dict[str, Any],
        id_key: str = 'id',
        full_content_key: str = 'full_content',
        title_key: str = 'title',
        level_key: str = 'level',
        entities_key: str = 'entity_ids',
        attributes_key: str = 'attributes',
    ) -> 'Community':
        """Create a new community from the dict data."""
        return Community(
            id=d[id_key],
            title=d[title_key],
            full_content=d[full_content_key],
            level=d[level_key],
            entity_ids=d.get(entities_key),
            attributes=d.get(attributes_key),
        )
