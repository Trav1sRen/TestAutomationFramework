from abc import ABCMeta, abstractmethod

from . import APIBaseObject


class SoapObjectBase(APIBaseObject, metaclass=ABCMeta):
    default_headers = {'Content-Type': 'text/xml; charset=UTF-8',
                       'SOAPAction': 'http://schemas.xmlsoap.org/soap/envelope'}

    @abstractmethod
    def append_headers(self):
        pass
