import configparser
from functools import wraps
from platform import system

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from .err_msg import WAIT_TIME_OUT
from ..utils import proj_root

# Reader of project config file (.ini)
config = configparser.ConfigParser()
config.read(proj_root + '/test_config.ini')


def non_private_vars(cls):
    d = cls.__dict__
    return [d[key] for key in filter(lambda k: not k.startswith('__'), d)]


ALLOWED_LOC_TYPES = non_private_vars(By)


def fluent_wait(driver, selector, *, sel_type=By.CSS_SELECTOR, unique_loc=True):
    """
    Fluent wait until element is found within timeout limit
    :param driver: current running driver
    :param selector: locator of the element to be found
    :param sel_type: locator type (recommend to use By class variable)
    :param unique_loc: flag to decide if returning single element other than list of elements
    :return: obtained web element(s)
    """

    if isinstance(selector, tuple):  # Return value of <get_loc> in page object
        selector, sel_type = selector

    try:
        timeout = int(config['TEST_CONTROL']['WAIT_TIME_OUT'])
    except KeyError:
        timeout = 30

    try:
        poll_frequency = int(config['TEST_CONTROL']['POLL_FREQUENCY'])
    except KeyError:
        poll_frequency = 1
    wait = WebDriverWait(driver, timeout, poll_frequency, (StaleElementReferenceException,))

    if unique_loc:
        def _expected(dri):
            ele = dri.find_element(sel_type, selector)
            return ele if ele.is_displayed() else False

        return wait.until(_expected, WAIT_TIME_OUT)
    else:
        def _expected(dri):
            ele_arr = dri.find_elements(sel_type, selector)
            for ele in ele_arr:
                if not ele.is_displayed():
                    return False
            return ele_arr

        return wait.until(_expected, WAIT_TIME_OUT)


def check_os():
    """
    Check current platform running on
    :return: tuple of directory name to load the matched driver and the extend name of file
    """
    if system() == 'Linux':
        return 'linux', ''
    elif system() == "Darwin":
        return 'mac', ''
    elif system() == "Windows":
        return 'win', '.exe'


def _webwait(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sel_type = kwargs.get('sel_type', By.CSS_SELECTOR)
        if sel_type not in ALLOWED_LOC_TYPES:
            raise ValueError('Unknown locator type %s' % sel_type)
        return func(*args, **kwargs)

    return wrapper


web_fluent_wait = _webwait(fluent_wait)
