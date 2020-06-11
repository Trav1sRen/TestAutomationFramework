import json
import re
from abc import ABCMeta, abstractmethod

import lxml.etree as et

from src.objects import BaseObject
from src.utils import proj_root, typeassert, var_dict


class APIBaseObject(BaseObject, metaclass=ABCMeta):
    default_headers = {}  # default request headers
    soap_skin = None  # not overwriting if pure xml other than SOAP request
    endpoint = None  # overwrite by each API obj

    def __init__(self, rq_name):
        # current environment
        self.env = ''

        # container for env variables
        self.envs = []

        # load global variables into container
        with open(proj_root + '/env/globals.json') as f:
            self.globals = json.load(f)

        # post url
        self.url = ''

        # current rq name
        self.rq_name = rq_name

        # request xml str(convert from json)
        self.rq_body = ''

    @staticmethod
    def _set_attribute_for_node(ele, attr_dict):
        """
        Set attributes for specific node
        :param ele: xml node to set the attributes
        :param attr_dict: attribute dict to append onto the node
        :return: None
        """

        if attr_dict:
            for key, val in attr_dict.items():
                ele.set(key, val)

    @typeassert(rq_dict=dict)
    def assemble_request_xml(self, rq_name, rq_dict, **root_attrs):
        """
        Assemble the request xml body
        :param rq_name: name of the root
        :param rq_dict: dict parsed from the request json
        :param root_attrs: attributes on root node
        :return: None
        """
        root = et.Element(rq_name, **root_attrs)

        for key, value in rq_dict.items():
            cur_ele = root
            for node in key.split('.'):
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
                        sub_ele = et.SubElement(cur_ele, node)
                        self._set_attribute_for_node(sub_ele, attr_dict)
                        cur_ele = sub_ele
                    else:
                        cur_ele = cur_ele.findall('.//' + node)[index]
                elif cur_ele.find(node) is not None:
                    cur_ele = cur_ele.find(node)
                else:
                    sub_ele = et.SubElement(cur_ele, node)
                    self._set_attribute_for_node(sub_ele, attr_dict)
                    cur_ele = sub_ele
            cur_ele.text = value

        if self.soap_skin:
            self.rq_body = self.soap_skin % (et.tostring(root, encoding='unicode'))

    def append_headers(self, **extras):
        """
        Append new headers based on various situations
        :param extras: extra headers
        :return: None
        """
        self.default_headers.update(extras)

    def set_env(self, env):
        """
        Set current environment and load env variables
        :param env: current environment for execution
        :return: None
        """

        self.env = env
        with open(proj_root + '/env/' + env + '.json') as f_obj:
            self.envs = json.load(f_obj)

        # define post url depending on the environment
        self.url = '/'.join(
            (self._get_property_from_variables('BaseUrl'), self._get_property_from_variables('Context'), self.endpoint))

    def unpack_json(self, *file_names, json_name):
        """
        Load json body from files
        :param file_names: a tuple of files in which json need to be combined
        :param json_name: json name to load in the json file that has the same name with RQ
        :return: rq dict which has loaded the variables from session
        """

        d = {}
        for name in file_names:
            d = self._load_json(d, name, json_name)

        return self._load_variables(d)

    @abstractmethod
    def _load_json(self, d, name, json_name):
        """
        Customize the logic of loading multiple json files
        :param d: default base dict to append on
        :param name: json file name
        :param json_name: json obj name
        :return: the instance of ChainMap
        """

        pass

    def _load_variables(self, d):
        patt = r'{{(.*?)}}'
        return dict((k, v) for k, v in zip(
            d.keys(), (re.sub(
                patt, lambda match: self._get_property_from_variables(match.group(1)), val) for val in d.values())))

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
