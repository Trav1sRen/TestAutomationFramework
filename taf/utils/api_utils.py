import base64
import json
import logging
import re
import sys
from abc import ABCMeta, abstractmethod
from functools import wraps
from inspect import signature

import jsonschema
import lxml.etree as et
import xmltodict

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# default encoding
encoding = 'utf-8'

# container for temporary variables
var_dict = {}


def is_debug():
    # Judge if running under the debug mode
    gettrace = getattr(sys, 'gettrace', None)
    if gettrace is None:
        return False
    elif gettrace():
        return True
    else:
        return False


# Get rootpath of the project which uses the framework as dependency
proj_root = sys.path[2] if is_debug() else sys.path[1]


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
    """ Decorator to implement the type check upon arguments
    (no need to consider about the 'self' parameter) """

    def decorator(func):
        sig = signature(func)
        bound_types = sig.bind_partial(*tyargs, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs).arguments
            for key, val in bound_values.items():
                if key in bound_types:
                    if not isinstance(val, bound_types[key]):
                        raise TypeError(
                            'Parameter <%s> must be the type of %s' % (key, bound_types[key]))
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


class SchemaValidator(metaclass=ABCMeta):
    @typeassert(str)
    def __init__(self, body, schema_path):
        """
        Validate the response xml body against schema file
        :param body: str body to be verified
        :param schema_path: path of the schema file inside 'proj_root/schema/' folder to check against
        """

        self._body = body

        m = re.match(r'.+/(.+?)\.(json|xsd)', schema_path)
        if not m:
            raise ValueError('Schema path does not match the pattern.')
        self._schema_name = m.group(1)

        # open and read schema file
        with open(proj_root + '/schema/' + schema_path) as schema_file:
            self._schema_to_check = schema_file.read()

    @typeassert(log=str)
    def _write_log(self, prefix, log):
        with open(proj_root + 'log/' + prefix + self._schema_name + '.log', 'w') as error_log_file:
            error_log_file.write(log)

    @abstractmethod
    def validate_schema(self):
        pass


class JsonValidator(SchemaValidator):
    def validate_schema(self):
        checker = jsonschema.FormatChecker()
        validator = jsonschema.validators.Draft6Validator(json.loads(self._schema_to_check), format_checker=checker)

        msg = []
        iter_errors = validator.iter_errors(json.loads(self._body))

        if not iter_errors:
            for err in iter_errors:
                field_name = '-'.join(err.absolute_path)
                msg.append('Validate Error, flied[%s], error msg: %s' % (field_name, err.message))

        if not msg:
            logger.info('JSON valid, schema validation ok.')
        else:
            logger.error('JSON schema validation error, see error_jsonschema.log')
            self._write_log('error_jsonschema_', '\n'.join(msg))


class XmlValidator(SchemaValidator):
    def validate_schema(self):
        xmlschema_doc = et.fromstring(self._schema_to_check)
        xmlschema = et.XMLSchema(xmlschema_doc)

        # parse xml
        doc = None
        try:
            doc = et.fromstring(self._body)
            logger.info('XML well formed, syntax ok.')

        # check for XML syntax errors
        except et.XMLSyntaxError as err:
            logger.error('XML Syntax Error, see error_syntax.log')
            self._write_log('error_syntax_', str(err))

        # validate against schema
        if doc is not None:
            try:
                xmlschema.assertValid(doc)
                logger.info('XML valid, schema validation ok.')

            except et.DocumentInvalid:
                logger.error('XML schema validation error, see error_xmlschema.log')
                self._write_log('error_xmlschema_', str(xmlschema.error_log))
