import lxml.etree as et

from taf import NotInstantiated
from taf.utils import typeassert, CustomDict, xml2dict, encoding
from . import APIBaseObject


class SoapBaseObject(APIBaseObject, metaclass=NotInstantiated):
    soap_skin = '%s'  # need to be overwritten by each API obj
    default_headers = {'Content-Type': 'text/xml; charset=UTF-8',
                       'SOAPAction': 'http://schemas.xmlsoap.org/soap/envelope'}

    def __init__(self, rq_name):
        # current rq name
        self.rq_name = rq_name

        super(SoapBaseObject, self).__init__()

    @typeassert(rq_dict=dict)
    def assemble_soap_xml(self, rq_dict, **root_attrs):
        """
        Assemble the request xml body
        :param rq_dict: dict parsed from the json file
        :param root_attrs: attributes on root node
        """

        root = et.Element(self.rq_name, **root_attrs)
        root = self._flatjson2xml(root, rq_dict)
        self.rq_body = self.soap_skin % (et.tostring(root).decode(encoding))

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
