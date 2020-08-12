import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from functools import reduce, partial
import re
import json
from json.decoder import JSONDecodeError

from lxml.etree import XMLSyntaxError

from taf.utils import typeassert, CustomDict, xml2dict, cannot_be_instantiated
from . import APIBaseObject


class RestBaseObject(APIBaseObject):
    __new__ = partial(cannot_be_instantiated, name='RestBaseObject')

    def unflatten_json(self, rq_dict):
        """
        Convert the flat json to nested json
        :param rq_dict: dict parsed from the json file
        """

        tmp = 0
        patt = re.compile(r'(\w+)\[(\d+)\]')

        def _traversal(o, k):
            m = re.match(patt, k)

            nonlocal tmp
            if m:
                k, i = m.groups()
                tmp = int(i)
                return o.setdefault(k, [])
            else:
                if isinstance(o, list):
                    o.insert(tmp, {k: {}})
                    return o[tmp][k]  # must return the view
                else:
                    return o.setdefault(k, {})

        output = {}
        for key, val in rq_dict.items():
            path = key.split(self.delimiter)

            if re.match(patt, path[-1]):
                raise ValueError('Last key of path should not contain index')

            obj = reduce(_traversal, path[:-1], output)
            if isinstance(obj, list):
                obj.insert(tmp, {path[-1]: val})
            else:
                obj[path[-1]] = val

        self.rq_body = json.dumps(output, indent=4)  # for pretty print

    @typeassert(rs_body=str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: <rs_body> attr in RestBaseClient
        """

        self.rs_body = rs_body
        try:
            self._rs_dict = CustomDict(json.loads(rs_body))
        except JSONDecodeError:
            try:
                self._rs_dict = CustomDict(xml2dict(rs_body))
            except XMLSyntaxError:
                logger.warning('Response str could be neither parsed to json nor xml obj')

    def process_response(self):
        raise NotImplementedError('You must customize the logic when processing the response')
