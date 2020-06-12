from src.objects import NotInstantiated
from src.utils import typeassert, CustomDict, convert_xml_to_dict
from . import APIBaseObject


class SoapObjectBase(APIBaseObject, metaclass=NotInstantiated):
    default_headers = {'Content-Type': 'text/xml; charset=UTF-8',
                       'SOAPAction': 'http://schemas.xmlsoap.org/soap/envelope'}

    @typeassert(rs_body=str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: response str
        :return: a dict whose instance is CustomDict
        """

        return CustomDict(convert_xml_to_dict(rs_body, trim_ns=True))

    def process_response(self, rs_dict):
        raise NotImplementedError('You must customize the logic when processing the response')