import inspect
from functools import partial
from functools import wraps

from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By

from taf.utils import fluent_wait, ALLOWED_LOC_TYPES, non_private_vars
from .android import AndroidDevices

ALLOWED_MOBILE_LOC_TYPES = list(non_private_vars(MobileBy)) + [By.XPATH, By.ID, By.CLASS_NAME]


def _appwait(func):
    @wraps(func)
    def wrapper(*args, webview=False, **kwargs):
        sel_type = kwargs.get('sel_type', By.XPATH)
        if not webview:
            if sel_type not in ALLOWED_MOBILE_LOC_TYPES:
                raise ValueError('Argument of <sel_type> is not legal for app non-webview testing')
        else:
            if sel_type not in ALLOWED_LOC_TYPES:
                raise ValueError('Argument of <sel_type> is not legal for app webview testing')
        return func(*args, **kwargs)

    sig = inspect.signature(func)
    parms = list(sig.parameters.values())
    parms.append(inspect.Parameter('webview', inspect.Parameter.KEYWORD_ONLY, default=False))
    wrapper.__signature__ = sig.replace(parameters=parms)

    return wrapper


app_fluent_wait = _appwait(partial(fluent_wait, sel_type=By.XPATH))
