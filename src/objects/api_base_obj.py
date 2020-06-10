import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import re

from abc import abstractmethod

import lxml.etree as et

from src.utils import proj_root, encoding
from .base_obj import BaseObject


def set_attribute_for_node(ele, attr_dict):
    if attr_dict:
        for key, val in attr_dict.items():
            ele.set(key, val)


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


class APIBaseObject(BaseObject):
    rq_body = None
    rs_body = None

    soap_skin = None  # not overwriting if pure xml other than SOAP request

    @abstractmethod
    def set_headers(self):
        pass

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
