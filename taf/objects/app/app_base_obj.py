import inspect
import re
from functools import wraps, partial
from inspect import signature

from taf.objects.web import PageBaseObject
from taf.utils import inject_sig, cannot_be_instantiated
from taf.utils.app_utils import ALLOWED_MOBILE_LOC_TYPES


def webview_support(func):
    """ Decorator makes set/get locators support webview """

    @wraps(func)
    def wrapper(*args, webview=False, **kwargs):
        if webview:
            i = [x.strip() for x in re.match(
                r'\((.*?)\)', str(signature(func))).group(1).split(',')].index('name')

            args = list(args)
            args[i] = '*' + args[i]

        return func(*args, **kwargs)

    inject_sig(func, wrapper, 'webview', inspect.Parameter.KEYWORD_ONLY, default=False)
    return wrapper


class AppBaseObject(PageBaseObject):
    _allowed_locs = ALLOWED_MOBILE_LOC_TYPES

    __new__ = partial(cannot_be_instantiated, name='AppBaseObject')

    @webview_support
    def _set_loc(self, name, loc, loc_type):
        """ If wanna save a webview locator, add keyword arg 'webview=True',
            and the name of webview locator will have a '*' as prefix """

        return super()._set_loc(name, loc, loc_type)

    @webview_support
    def get_loc(self, name, *, loc_type):
        """ If wanna get a webview locator, add keyword arg 'webview=True',
            and the name of locator with a '*' prefix will be fetched """

        return super().get_loc(name, loc_type=loc_type)
