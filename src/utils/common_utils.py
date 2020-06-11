import base64
import configparser
from inspect import signature

import rootpath

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
