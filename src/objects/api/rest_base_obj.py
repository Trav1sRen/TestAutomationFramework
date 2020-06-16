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


class RestBaseObject(APIBaseObject, metaclass=NotInstantiated):
    def unflatten_json(self, rq_dict):
        """
        Convert the flat json to nested json
        :param rq_dict: dict parsed from the json file
        """

        def _get_nested_default(d, path_):
            return reduce(lambda d_, k: d_.setdefault(k, {}), path_, d)

        def _set_nested(d, path_, value):
            _get_nested_default(d, path_[:-1])[path_[-1]] = value

        output = {}
        for key, val in rq_dict.items():
            path = key.split(self.delimiter)
            _set_nested(output, path, val)

        self.rq_body = json.dumps(output, indent=4)  # for pretty print

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
