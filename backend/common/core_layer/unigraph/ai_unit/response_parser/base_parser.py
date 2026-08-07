from abc import ABC, abstractmethod


class ResponseParser(ABC):
    @staticmethod
    @abstractmethod
    def parse(response: dict, **kwargs) -> dict:
        pass
