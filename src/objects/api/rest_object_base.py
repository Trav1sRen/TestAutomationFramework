import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from functools import reduce
import json
from json.decoder import JSONDecodeError

from lxml.etree import XMLSyntaxError

from src import NotInstantiated
from src.utils import typeassert, CustomDict, xml2dict
from . import APIBaseObject


class RestObjectBase(APIBaseObject, metaclass=NotInstantiated):
    def unflatten_json(self, rq_dict):
        """
        Convert the flat json to nested json
        :param rq_dict: dict parsed from the json file
        """

        def _get_nested_default(d, path):
            return reduce(lambda d, k: d.setdefault(k, {}), path, d)

        def _set_nested(d, path, value):
            _get_nested_default(d, path[:-1])[path[-1]] = value

        output = {}
        for k, v in rq_dict.items():
            path = k.split(self.delimiter)
            _set_nested(output, path, v)

        self.rq_body = json.dumps(output)

    @typeassert(rs_body=str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: response str
        :rtype: src.utils.CustomDict
        """

        try:
            return CustomDict(json.loads(rs_body))
        except JSONDecodeError:
            try:
                return CustomDict(xml2dict(rs_body))
            except XMLSyntaxError:
                logger.warning('Response str could be neither parsed to json nor xml obj')
                return rs_body

    def process_response(self, rs):
        raise NotImplementedError('You must customize the logic when processing the response')
