import json
import logging
import re
from functools import reduce, partial
from json.decoder import JSONDecodeError

from lxml.etree import XMLSyntaxError

from taf.utils import typeassert, CustomDict, xml2dict, cannot_be_instantiated
from . import APIBaseObject

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RestBaseObject(APIBaseObject):
    __new__ = partial(cannot_be_instantiated, name='RestBaseObject')

    def unflatten_json(self):
        """
        Convert the flat json to nested json
        """

        tmp = 0
        patt = re.compile(r'(\w+)\[(\d+)]')

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

        for key, val in self._flat_dict.items():
            path = key.split(self.delimiter)

            if re.match(patt, path[-1]):
                raise ValueError('Last key of path should not contain index')

            obj = reduce(_traversal, path[:-1], self.rq_dict)
            if isinstance(obj, list):
                obj.insert(tmp, {path[-1]: val})
            else:
                obj[path[-1]] = val

    @typeassert(str)
    def load_client_response(self, rs_body):
        """
        Load response from APIBaseClient instance and parse to dict
        :param rs_body: <rs_body> attr in RestBaseClient
        """

        try:
            self._rs_dict = CustomDict(json.loads(rs_body))
        except JSONDecodeError:
            try:
                self._rs_dict = CustomDict(xml2dict(rs_body))
            except XMLSyntaxError:
                logger.warning('Response str could be neither parsed to json nor xml obj')
        return self

    def process_response(self):
        raise NotImplementedError('You must customize the logic when processing the response')
