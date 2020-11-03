import configparser
import inspect
from collections.abc import Iterable

from .api_utils import CustomDict
from .api_utils import encoding, var_dict, proj_root
from .api_utils import typeassert, xml2dict, validate_schema
from .err_msg import *
from .web_utils import check_os, fluent_wait, web_fluent_wait, non_private_vars, ALLOWED_LOC_TYPES

# Reader of project config file (.ini)
config = configparser.ConfigParser()
config.read(proj_root + '/test_config.ini')


def flat_map(seq, func=None):
    """
    Customized flatMap method similar with JavaScript
    :param seq: Flattened data
    :param func: function working on the subelement
    :return: the generator object
    """

    if not isinstance(seq, (list, tuple, set)):
        raise TypeError('Flattened data could only be one of <list>, <tuple> or <set>')
    for sub in seq:
        if isinstance(sub, Iterable) and not isinstance(sub, (str, dict)):
            yield from flat_map(sub, func)
        else:
            if func is None:
                yield sub
            else:
                r = func(sub)
                try:
                    yield from flat_map(r)  # flatten the return value of func as well
                except TypeError:
                    yield r


def inject_sig(func, wrapper, *args, **kwargs):
    """ Add extra param into wrapped func's signature """

    sig = inspect.signature(func)
    parms = list(sig.parameters.values())
    parms.append(inspect.Parameter(*args, **kwargs))
    wrapper.__signature__ = sig.replace(parameters=parms)


def cannot_be_instantiated(cls, name):
    """ method to prevent cls from being instantiated """
    if cls.__name__ == name:
        raise TypeError(CANNOT_BE_INSTANTIATED % cls)

    return object.__new__(cls)
