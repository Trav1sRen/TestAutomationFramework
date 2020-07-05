import inspect
import os
import re
from functools import partial
from functools import wraps

from selenium.webdriver.common.by import By

from taf.utils import fluent_wait


class AndroidDevices:
    def __init__(self):
        self.udids = []
        for line in os.popen('adb devices').readlines()[1:-1]:
            udid = re.findall(r'^\w*\b', line)[0]
            self.udids.append(udid)

    @property
    def versions(self):
        """ Get the os version of connected devices """

        return list(map(lambda udid: os.popen(
            'adb -s %s shell getprop ro.build.version.release' % udid).readlines()[0].strip('\n'), self.udids))

    @property
    def device_names(self):
        """ Get the product name of connected devices (Sometimes unnecessary) """

        return list(map(lambda udid: os.popen(
            'adb -s %s shell getprop ro.product.model' % udid).readlines()[0].strip('\n'), self.udids))


def _optional_webview(func):
    @wraps(func)
    def wrapper(*args, webview=False, **kwargs):
        if not webview:
            if kwargs['sel_type'] not in (By.XPATH, By.ID, By.CLASS_NAME):
                raise ValueError('Argument <sel_type> is not legal for app non-webview testing')
        return func(*args, **kwargs)

    sig = inspect.signature(func)
    parms = list(sig.parameters.values())
    parms.append(inspect.Parameter('webview', inspect.Parameter.KEYWORD_ONLY, default=False))
    wrapper.__signature__ = sig.replace(parameters=parms)

    return wrapper


app_fluent_wait = _optional_webview(partial(fluent_wait, sel_type=By.XPATH))
