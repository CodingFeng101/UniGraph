from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .named import Named


@dataclass
class Entity(Named):
    """A protocol for an entity in the system."""

    type: Optional[str] = None
    """Type of the entity (can be any string, optional)."""

    attributes_embedding: Optional[List[float]] = None
    """The semantic (i.e. text) embedding of the entity (optional)."""

    community_ids: Optional[List[str]] = None
    """The community IDs of the entity (optional)."""

    rank: Optional[int] = 1
    """Rank of the entity, used for sorting (optional). Higher rank indicates more important entity. This can be based on centrality or other metrics."""

    attributes: Optional[Dict[str, Any]] = None
    """Additional attributes associated with the entity (optional), e.g. start time, end time, etc. To be included in the search prompt."""

    @classmethod
    def from_dict(
        cls,
        d: dict[str, Any],
        id_key: str = 'id',
        name_key: str = 'name',
        type_key: str = 'type',
        community_key: str = 'community',
        rank_key: str = 'degree',
        attributes_key: str = 'attributes',
    ) -> 'Entity':
        """Create a new entity from the dict data."""
        return Entity(
            id=d[id_key],
            name=d[name_key],
            type=d.get(type_key),
            community_ids=d.get(community_key),
            rank=d.get(rank_key, 1),
            attributes=d.get(attributes_key),
        )
