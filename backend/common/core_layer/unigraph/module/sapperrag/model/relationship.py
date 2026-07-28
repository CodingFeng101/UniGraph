from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .identified import Identified


@dataclass
class Relationship(Identified):
    """A relationship between two entities. This is a generic relationship, and can be used to represent any type of relationship between any two entities."""

    source: str
    """The source entity name."""

    target: str
    """The target entity name."""

    type: Optional[str] = None
    """The type of the relationship (optional)."""

    name: Optional[str] = None
    """The name of the relationship (optional)."""

    weight: Optional[float] = 1.0
    """The edge weight."""

    attributes: Optional[Dict[str, Any]] = None
    """Additional attributes associated with the relationship (optional). To be included in the search prompt"""

    triple_source: Optional[str] = None
    """Triplet information source"""

    @classmethod
    def from_dict(
        cls,
        d: Dict[str, Any],
        id_key: str = 'id',
        type_key: str = 'type',
        source_key: str = 'source',
        target_key: str = 'target',
        weight_key: str = 'weight',
        attributes_key: str = 'attributes',
        triple_source_key: str = 'triple_source',
    ) -> 'Relationship':
        """Create a new relationship from the dict data."""
        return Relationship(
            id=d[id_key],
            type=d.get(type_key),
            source=d[source_key],
            target=d[target_key],
            weight=d.get(weight_key, 1.0),
            attributes=d.get(attributes_key),
            triple_source=d.get(triple_source_key),
        )
