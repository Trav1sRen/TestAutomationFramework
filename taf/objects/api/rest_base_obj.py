import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from functools import reduce
import re
import json
from json.decoder import JSONDecodeError

from lxml.etree import XMLSyntaxError

from taf.utils import typeassert, CustomDict, xml2dict
from . import APIBaseObject


class RestBaseObject(APIBaseObject):
    def __new__(cls, *args, **kwargs):
        if cls is RestBaseObject:
            raise TypeError('Cannot directly instantiate the base class %s' % cls)
        return object.__new__(cls)

    def unflatten_json(self, rq_dict):
        """
        Convert the flat json to nested json
        :param rq_dict: dict parsed from the json file
        """

        tmp = 0
        patt = re.compile('(\w+)\[(\d+)\]')

        def _traversal(obj, key):
            m = re.match(patt, key)

            nonlocal tmp
            if m:
                key, i = m.groups()
                tmp = int(i)
                return obj.setdefault(key, [])
            else:
                if isinstance(obj, list):
                    obj.insert(tmp, {key: {}})
                    return obj[tmp][key]  # must return the view
                else:
                    return obj.setdefault(key, {})

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
            self.rs_dict = CustomDict(json.loads(rs_body))
        except JSONDecodeError:
            try:
                self.rs_dict = CustomDict(xml2dict(rs_body))
            except XMLSyntaxError:
                logger.warning('Response str could be neither parsed to json nor xml obj')

    def process_response(self):
        raise NotImplementedError('You must customize the logic when processing the response')
