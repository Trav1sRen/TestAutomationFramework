from taf.utils import typeassert, CustomDict, xml2dict
from . import APIBaseObject


class SoapBaseObject(APIBaseObject):
    default_headers = {'Content-Type': 'text/xml; charset=UTF-8',
                       'SOAPAction': 'http://schemas.xmlsoap.org/soap/envelope'}

    def __new__(cls, *args, **kwargs):
        if cls is SoapBaseObject:
            raise TypeError('Cannot directly instantiate the base class %s' % cls)
        return object.__new__(cls)

    def rq_str2dict(self):
        """ Convert request str data to dict """
        return CustomDict(xml2dict(self.rq_body, trim_ns=True))

    @typeassert(rs_body=str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: <rs_body> attr in SoapBaseClient
        """

        self.rs_dict = CustomDict(xml2dict(rs_body, trim_ns=True))

    def process_response(self):
        raise NotImplementedError('You must customize the logic when processing the response')
