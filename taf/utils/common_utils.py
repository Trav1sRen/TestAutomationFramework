import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import base64
from inspect import signature

import lxml.etree as et
import xmltodict
import sys

# default encoding
encoding = 'utf-8'

# container for temporary variables
var_dict = {}

# Get rootpath of the project which uses the framework as dependency
proj_root = sys.path[1]


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
    Decorator to implement the type check upon arguments
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
def xml2dict(xml, strip_ns=False):
    """
    Convert xml str to dict
    :param xml: xml str about to be processed
    :param strip_ns: flag to decide if stripping the ns
    :rtype: dict
    """

    def _strip_ns(s):
        """
        Remove the namespace of xml str
        :return: xml str without namespaces
        """

        root = et.fromstring(s)
        for ele in root.xpath('descendant-or-self::*'):
            if ele.prefix:
                ele.tag = et.QName(ele).localname
        return et.tostring(root).decode(encoding)

    result = _strip_ns(xml) if strip_ns else xml
    return xmltodict.parse(result)


@typeassert(str)
def validate_schema(rs_body, schema_name):
    """
    Validate the response xml body against schema file
    :param rs_body: response str
    :param schema_name: name of the schema file to check against
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
