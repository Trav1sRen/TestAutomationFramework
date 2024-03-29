import json
import re
from functools import partial

import lxml.etree as et

from taf.utils import typeassert, CustomDict, xml2dict, var_dict, proj_root, encoding, cannot_be_instantiated


class APIBaseObject:
    delimiter = '.'  # delimiter of the json keys in json file

    default_headers = {}  # default request headers

    endpoint = ''  # overwritten by each API obj

    soap_skin = ''  # overwritten by each API obj

    rq_body = ''  # assembled request body

    __new__ = partial(cannot_be_instantiated, name='APIBaseObject')

    def __init__(self, env, rq_name=None):
        with open(proj_root + '/env/globals.json') as f1:
            self.globals = json.load(f1)  # container for global variables

        with open(proj_root + '/env/' + env + '.json') as f2:
            self.envs = json.load(f2)  # container for env variables

        # request url
        self.url = '/'.join(
            (self._get_property_from_variables('BaseUrl'),
             self._get_property_from_variables('Context'), self.endpoint))

        # name of root node when request data is in xml format
        if rq_name:
            self._rq_name = rq_name

        self._flat_dict = {}  # flat dict parsed from the json file

        self.rq_dict, self._rs_dict = {}, {}  # parsed from rq_body and rs_body

    @typeassert(ns_attrs=dict, nsmap=dict)
    def construct_xml(self, soap=False, ns_attrs=None, nsmap=None, **attrs):
        """ Assemble the request xml body """

        if soap:
            if not self.soap_skin:
                raise ValueError(
                    'class variable "soap_skin" should be overwritten by str containing "%s"')

        attrib = {}
        if ns_attrs:
            for key, val in ns_attrs:
                keys = key.split(':')
                if len(keys) == 1:
                    raise ValueError('<%s> is not in the correct format' % key)

                attr_qname = et.QName(nsmap[keys[0]], keys[1])
                attrib[attr_qname] = val

        if nsmap is None:
            nsmap = {}

        root = et.Element(self._rq_name, attrib, nsmap, **attrs)
        root = self._flatjson2xml(root, self._flat_dict, nsmap)

        raw = et.tostring(root).decode(encoding)
        self.rq_body = self.soap_skin % raw if soap else raw

    def _flatjson2xml(self, root, rq_dict, nsmap):
        """
        Assemble the request xml body
        :param root: node of root element
        :param rq_dict: dict parsed from the json file
        """

        def _create_subelement(ele, name):
            """ Create sub-element for current node """

            m = re.match(r'(\w+):(\w+)', name)
            if m:
                ns, tag = m.groups()
                return et.SubElement(ele, nsmap[ns] + tag)
            else:
                return et.SubElement(ele, name)

        def _setattrs(ele, d):
            """ Set attributes for specific node """

            if d:
                for k, v in d.items():
                    ele.set(k, v)

        for key, value in rq_dict.items():
            cur_ele = root
            for node in key.split(self.delimiter):
                attr_dict = {}

                patt = r'(.*?)\((.*?)\)'
                match = re.search(patt, node)
                if bool(match):
                    kv_groups = match.group(2).split(',')
                    for kv in kv_groups:
                        kv = kv.strip()
                        attr_key, attr_val = kv.split('=')
                        attr_dict[attr_key.strip()] = attr_val.strip().replace('\'', '')
                    node = match.group(1)

                patt = r'(.*?)\[(.*?)\]'
                match = re.match(patt, node)
                if bool(match):
                    index = int(match.group(2))
                    node = match.group(1)
                    if len(cur_ele.findall('.//' + node)) == index:
                        sub_ele = _create_subelement(cur_ele, node)
                        _setattrs(sub_ele, attr_dict)
                        cur_ele = sub_ele
                    else:
                        cur_ele = cur_ele.findall('.//' + node)[index]
                elif cur_ele.find(node) is not None:
                    cur_ele = cur_ele.find(node)
                else:
                    sub_ele = _create_subelement(cur_ele, node)
                    _setattrs(sub_ele, attr_dict)
                    cur_ele = sub_ele
            cur_ele.text = value

        return root

    def append_headers(self, **extras):
        """
        Append new headers based on various situations
        :param extras: extra headers
        """
        self.default_headers.update(self._load_variables(extras))

    @typeassert(dict, j=dict)
    def unpack_json(self, kwargs=None, *, j=None):
        """
        Load json body from files
        :param kwargs: mapping of json file name and jsonobj name
        :param j: use specified json body instead of reading from file
        """

        kwargs = kwargs or {}

        d = j or {}
        for file_name, obj_name in kwargs.items():
            with open(proj_root + '/json/%s.json' % file_name) as file_obj:
                tmp_d = json.load(file_obj)
                obj = tmp_d[obj_name] if obj_name is not None else tmp_d
                d.update(obj)

        self._flat_dict = self._load_variables(d)
        return self

    def _load_variables(self, d):
        patt = r'{{(.*?)}}'
        return dict((k, v) for k, v in zip(
            d.keys(), (re.sub(
                patt, lambda match: self._get_property_from_variables(
                    match.group(1)), val) for val in d.values())))

    def _get_property_from_variables(self, var_key):
        """
        Get property from variables(globals > envs > var_dict)
        :param var_key: specify the reference key of the variable to be obtained
        :return: obtained mapping value
        """

        match = list(filter(lambda ele: ele['key'] == var_key and ele['enabled'], self.globals))
        if match:
            return match[0]['value']
        else:
            match = list(filter(lambda ele: ele['key'] == var_key and ele['enabled'], self.envs))
            if match:
                return match[0]['value']
            elif var_key in var_dict.keys():
                return var_dict[var_key]
            else:
                raise KeyError('Environment key [' + var_key + '] is not found in variables')

    def rq_str2dict(self):
        """ Convert request str data to dict """

        if self.rq_dict:
            self.rq_dict = CustomDict(self.rq_dict)
        else:
            self.rq_dict = CustomDict(xml2dict(self.rq_body, strip_ns=True))
