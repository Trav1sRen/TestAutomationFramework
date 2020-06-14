import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import json
from json.decoder import JSONDecodeError

from lxml.etree import XMLSyntaxError

from src import NotInstantiated
from src.utils import typeassert, CustomDict, convert_xml_to_dict
from . import APIBaseObject


class RestObjectBase(APIBaseObject, metaclass=NotInstantiated):
    def assemble_request_json(self, rq_dict):
        """
        Assemble the request json body from flat json
        :param rq_dict: dict parsed from the request json
        :return: None
        """

        self.rq_body = json.dumps(rq_dict)

    @typeassert(rs_body=str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: response str
        :return: a dict whose instance is CustomDict
        """

        try:
            return CustomDict(json.loads(rs_body))
        except JSONDecodeError:
            try:
                return CustomDict(convert_xml_to_dict(rs_body))
            except XMLSyntaxError:
                logger.warning('Response str could be neither parsed to json nor xml obj')
                return rs_body

    def process_response(self, rs):
        raise NotImplementedError('You must customize the logic when processing the response')
