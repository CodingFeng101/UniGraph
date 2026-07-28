from abc import ABC, abstractmethod


class BaseInstruction(ABC):
    def __init__(self):
        self.next_instruction = None

    def set_next(self, instruction):
        self.next_instruction = instruction

    @abstractmethod
    async def execute(self, **kwargs):
        # **kwargs参数自行处理
        pass
