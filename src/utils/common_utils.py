import configparser
from inspect import signature

import rootpath

proj_root = rootpath.detect()  # this is the project's root path

# retrieve project properties
config = configparser.ConfigParser()
config.read(proj_root + '/properties.ini')

encoding = config['API']['encoding']


def typeassert(*tyargs, **ty_kwargs):  # Decorator to implement the type check upon func args
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
