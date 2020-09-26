from functools import partial

from taf.utils import typeassert, CustomDict, xml2dict, cannot_be_instantiated
from . import APIBaseObject


class SoapBaseObject(APIBaseObject):
    default_headers = {'Content-Type': 'text/xml; charset=UTF-8',
                       'SOAPAction': 'http://schemas.xmlsoap.org/soap/envelope'}

    __new__ = partial(cannot_be_instantiated, name='SoapBaseObject')

    @typeassert(str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: <rs_body> attr in SoapBaseClient
        """

        self._rs_dict = CustomDict(xml2dict(rs_body, strip_ns=True))

    def process_response(self):
        raise NotImplementedError('You must customize the logic when processing the response')
