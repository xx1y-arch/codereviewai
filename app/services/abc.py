import logging

from abc import ABC, abstractmethod


class BaseService(ABC):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, *args, **kwargs):
        pass
