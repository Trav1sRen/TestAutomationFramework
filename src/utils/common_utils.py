import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import base64
import configparser
from inspect import signature

import lxml.etree as et
import rootpath
import xmltodict

proj_root = rootpath.detect()  # this is the project's root path

# retrieve project properties
config = configparser.ConfigParser()
config.read(proj_root + '/properties.ini')  # name is settled with 'properties.ini'

# default encode when parsing
encoding = config['API']['encoding']

# container for temporary variables
var_dict = {}


def generate_auth(username, pwd):
    """
    Generate the request authorization
    :param username: username for auth
    :param pwd: username for password
    :return: a "Basic" authorization
    """

    data_bytes = ('%s:%s' % (username, pwd)).encode(encoding)
    return 'Basic ' + base64.b64encode(data_bytes).decode(encoding)


def typeassert(*tyargs, **ty_kwargs):
    """
    Decorator to implement the type check upon func args
    :param tyargs: assert types for positional args
    :param ty_kwargs:  assert types for keyword-only args
    :return: Inner decorator func
    """

    def decorator(func):
        sig = signature(func)
        bound_types = sig.bind_partial(*tyargs, **ty_kwargs).arguments

        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs).arguments
            for key, val in bound_values.items():
                if key in bound_types:
                    if not isinstance(val, bound_types[key]):
                        raise TypeError('Argument %s must be %s' % (key, bound_types[key]))
            return func(*args, **kwargs)

        return wrapper

    return decorator


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


@typeassert(str)
def convert_xml_to_dict(xml_str, trim_ns=False):
    """
    Convert xml str to dict
    :param xml_str: xml str about to be processed
    :param trim_ns: flag to decide if trim the ns
    :return: a dict parsed from xml obj
    """

    def _strip_ns_prefix(s):
        """
        Remove the namespace of xml str
        :param s: xml str about to be processed
        :return: xml str without namespaces
        """

        root = et.fromstring(s)
        for ele in root.xpath('descendant-or-self::*'):
            if ele.prefix:
                ele.tag = et.QName(ele).localname
        return et.tostring(root).decode(encoding)

    result = _strip_ns_prefix(xml_str) if trim_ns else xml_str
    return xmltodict.parse(result)


@typeassert(str)
def validate_schema(rs_body, schema_name):
    """
    Validate the response xml body against schema file
    :param rs_body: response str
    :param schema_name: name of the schema file to check against
    :return: None
    """

    # open and read schema file
    with open(proj_root + '/schema/' + schema_name + '.xsd') as schema_file:
        schema_to_check = schema_file.read()
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
