import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import re
import lxml.etree as et
import xmltodict
from abc import ABCMeta, abstractmethod

from ..utils.common_utils import proj_root, encoding, typeassert
from .base_obj import BaseObject


class CustomDict(dict):
    def __getitem__(self, key):
        """
        Overwrite __getitem__ to return None instead of 'KeyError' when key has no mapping
        :param key: key used for mapping
        :return: mapping of the key (None if the key has no mapping)
        """

        try:
            val = super().__getitem__(key)
            if isinstance(val, dict):
                return CustomDict(val)
            elif isinstance(val, list):
                return list(map(lambda e: CustomDict(e) if isinstance(e, dict) else e, val))
            else:
                return val
        except KeyError:
            return None


def set_attribute_for_node(ele, attr_dict):
    """
    Set attributes for specific node
    :param ele: xml node to set the attributes
    :param attr_dict: attribute dict to append onto the node
    :return: None
    """

    if attr_dict:
        for key, val in attr_dict.items():
            ele.set(key, val)


def strip_ns_prefix(bytes_str):
    """
    Remove the namespace of xml string
    :param bytes_str: xml string in bytes about to be processed
    :return: xml string without namespaces
    """

    root = et.fromstring(bytes_str)
    for ele in root.xpath('descendant-or-self::*'):
        if ele.prefix:
            ele.tag = et.QName(ele).localname
    return et.tostring(root, encoding=encoding)


@typeassert(bytes)
def convert_xml_to_dict(bytes_str):
    """
    Convert xml string to dict
    :param bytes_str: xml string in bytes about to be processed
    :return: instance of CustomDict
    """

    new_str = strip_ns_prefix(bytes_str)
    d = xmltodict.parse(new_str)
    return CustomDict(d)


def validate_schema(rs_body, schema_name, path='/schema/'):
    # open and read schema file
    with open(proj_root + path + schema_name + '.xsd', encoding=encoding) as schema_file:
        schema_to_check = schema_file.read().encode(encoding)
    xmlschema_doc = et.fromstring(schema_to_check)
    xmlschema = et.XMLSchema(xmlschema_doc)

    # parse xml
    doc = None
    try:
        doc = et.fromstring(rs_body)
        logger.info('XML well formed, syntax ok.')

    # check for XML syntax errors
    except et.XMLSyntaxError as err:
        logger.error('XML Syntax Error, see error_syntax.log')
        with open('proj_root + log/error_syntax_' + schema_name + '.log', 'w') as error_log_file:
            error_log_file.write(str(err))

    # validate against schema
    if doc is not None:
        try:
            xmlschema.assertValid(doc)
            logger.info('XML valid, schema validation ok.')

        except et.DocumentInvalid:
            logger.error('Schema validation error, see error_schema.log')
            with open(proj_root + 'log/error_schema_' + schema_name + '.log', 'w') as error_log_file:
                error_log_file.write(str(xmlschema.error_log))


class APIBaseObject(BaseObject, metaclass=ABCMeta):
    rq_body, headers = None, None  # base attributes for a request

    soap_skin = None  # not overwriting if pure xml other than SOAP request

    @typeassert(rq_dict=dict)
    def assemble_request_xml(self, rq_name, rq_dict, **root_attrs):
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
                        set_attribute_for_node(sub_ele, attr_dict)
                        cur_ele = sub_ele
                    else:
                        cur_ele = cur_ele.findall('.//' + node)[index]
                elif cur_ele.find(node) is not None:
                    cur_ele = cur_ele.find(node)
                else:
                    sub_ele = et.SubElement(cur_ele, node)
                    set_attribute_for_node(sub_ele, attr_dict)
                    cur_ele = sub_ele
            cur_ele.text = value

        self.rq_body = self.soap_skin % (et.tostring(root, encoding='unicode'))

    @abstractmethod
    @typeassert(rs_dict=dict)
    def save_response(self, rs_dict):
        pass
