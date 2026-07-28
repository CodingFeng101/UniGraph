from abc import ABC, abstractmethod
from typing import Any, List


class BaseSearch(ABC):
    """The Base Search implementation."""

    def __init__(self, context_builder):
        self.context_builder = context_builder

    @abstractmethod
    def search(
        self, query: str, level: int, infer: bool, api_key: str, base_url: str, model: str, **kwargs: Any
    ) -> List[Any]:
        """Search for the given query.

        Args:
            api_key (str): api_key of User.
            base_url (str): base_url of User.
            query (str): The search query.
            level (int): The search level.
            infer (bool): Whether to infer the query.
            **kwargs (Any): Additional keyword arguments for the search.

        Returns:
            List[Any]: The search results.
        """

    @abstractmethod
    async def asearch(
        self, query: str, level: int, infer: bool, api_key: str, base_url: str, model: str, **kwargs: Any
    ) -> List[Any]:
        """Asynchronously search for the given query.

        Args:
            api_key (str): api_key of User.
            base_url (str): base_url of User.
            query (str): The search query.
            level (int): The search level.
            infer (bool): Whether to infer the query.
            **kwargs (Any): Additional keyword arguments for the search.

        Returns:
            List[Any]: The search results.
        """
