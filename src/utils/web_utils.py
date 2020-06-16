from platform import system

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait

from .common_utils import config


def fluent_wait(driver, selector, sel_type='css', find_single=True, timeout=config['WEB']['wait_timeout'],
                poll_frequency=config['WEB']['poll_frequency']):
    """
    Fluent wait until element is found within timeout limit
    :param driver: current running driver
    :param selector: locator of the element to be found
    :param sel_type: locator type
    :param find_single: flag to decide if returning single element other than list of elements
    :param timeout: time limit of element locating, raise TimeoutException if beyond the limit
    :param poll_frequency: time frequency of attempts to obtain
    :return: obtained web element(s)
    """
    wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency,
                         # commonly ignore exceptions below
                         ignored_exceptions=[NoSuchElementException, StaleElementReferenceException])

    if sel_type == 'css':
        if find_single:
            return wait.until(lambda dri: dri.find_element_by_css_selector(selector))
        else:
            return wait.until(lambda dri: dri.find_elements_by_css_selector(selector))
    elif sel_type == 'xpath':
        if find_single:
            return wait.until(lambda dri: dri.find_element_by_xpath(selector))
        else:
            return wait.until(lambda dri: dri.find_elements_by_xpath(selector))


def check_os():
    """
    Check current platform running on
    :return: directory name to load the matched driver
    """
    if system() == 'Linux':
        return 'linux'
    elif system() == "Darwin":
        return 'mac'
    elif system() == "Windows":
        return 'win'
