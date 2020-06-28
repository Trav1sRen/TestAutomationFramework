from taf.utils import typeassert, CustomDict, xml2dict
from . import APIBaseObject


class SoapBaseObject(APIBaseObject):
    default_headers = {'Content-Type': 'text/xml; charset=UTF-8',
                       'SOAPAction': 'http://schemas.xmlsoap.org/soap/envelope'}

    def __new__(cls, *args, **kwargs):
        raise TypeError('Cannot directly instantiate the base class <%s>' % cls.__name__)

    @typeassert(rs_body=str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: response in bytes
        :rtype: src.utils.CustomDict
        """

        return CustomDict(xml2dict(rs_body, trim_ns=True))

    @typeassert(rs=dict)
    def process_response(self, rs):
        raise NotImplementedError('You must customize the logic when processing the response')
