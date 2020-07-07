import inspect
from functools import partial
from functools import wraps

from selenium.webdriver.common.by import By

from taf.utils import fluent_wait
from .android import AndroidDevices


def _optional_webview(func):
    @wraps(func)
    def wrapper(*args, webview=False, **kwargs):
        if not webview:
            if kwargs['sel_type'] not in (By.XPATH, By.ID, By.CLASS_NAME):
                raise ValueError('Argument of <sel_type> is not legal for app non-webview testing')
        return func(*args, **kwargs)

    sig = inspect.signature(func)
    parms = list(sig.parameters.values())
    parms.append(inspect.Parameter('webview', inspect.Parameter.KEYWORD_ONLY, default=False))
    wrapper.__signature__ = sig.replace(parameters=parms)

    return wrapper


app_fluent_wait = _optional_webview(partial(fluent_wait, sel_type=By.XPATH))
