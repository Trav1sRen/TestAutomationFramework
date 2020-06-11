from src.utils import typeassert, encoding, CustomDict, convert_xml_to_dict
from . import APIBaseObject


class SoapObjectBase(APIBaseObject):
    default_headers = {'Content-Type': 'text/xml; charset=UTF-8',
                       'SOAPAction': 'http://schemas.xmlsoap.org/soap/envelope'}

    @typeassert(rs_body=str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: response str
        :return: a dict whose instance is CustomDict
        """

        return CustomDict(convert_xml_to_dict(bytes(rs_body, encoding=encoding), trim_ns=True))
