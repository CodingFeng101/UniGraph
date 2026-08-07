from abc import ABC, abstractmethod


class Indexer(ABC):
    """Base class for search context builders."""

    @abstractmethod
    def build_index(self, **kwargs):
        """Build search context."""
        pass
