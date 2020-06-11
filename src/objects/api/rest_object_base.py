from abc import ABCMeta, abstractmethod

from . import APIBaseObject


class RestObjectBase(APIBaseObject, metaclass=ABCMeta):
    @abstractmethod
    def append_headers(self):
        pass
