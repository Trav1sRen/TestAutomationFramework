import json
from abc import ABCMeta

from src.utils import typeassert, CustomDict, convert_xml_to_dict, encoding
from . import APIBaseObject


class RestObjectBase(APIBaseObject, metaclass=ABCMeta):
    @typeassert(rs_body=str)
    def load_client_response(self, rs_body, data_type='json'):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: response str
        :param data_type: obj type of response str
        :return: a dict whose instance is CustomDict
        """

        if data_type == 'json':
            return json.loads(rs_body)
        elif data_type == 'xml':
            return CustomDict(convert_xml_to_dict(bytes(rs_body, encoding=encoding)))

    def process_response(self, rs_dict):
        raise NotImplementedError('You must customize the logic when processing the response')
