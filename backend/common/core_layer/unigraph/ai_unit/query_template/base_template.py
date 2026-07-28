from abc import ABC, abstractmethod


class InstructionTemplate(ABC):
    @staticmethod
    @abstractmethod
    def get_template():
        pass

    @staticmethod
    @abstractmethod
    def render_template(**kwargs):
        pass
