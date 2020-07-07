from platform import system

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

ALLOWED_LOC_TYPES = list(By.__dict__.values())[2:-2]  # Supported locator types


def fluent_wait(driver, selector, *, sel_type=By.CSS_SELECTOR, find_single=True, timeout=10, poll_frequency=0.5):
    """
    Fluent wait until element is found within timeout limit
    :param driver: current running driver
    :param selector: locator of the element to be found
    :param sel_type: locator type (recommend to use By class variable)
    :param find_single: flag to decide if returning single element other than list of elements
    :param timeout: time limit of element locating, raise TimeoutException if beyond the limit
    :param poll_frequency: time frequency of attempts to obtain
    :return: obtained web element(s)
    """

    if isinstance(selector, tuple):  # Return value of <get_loc> in page object
        selector, sel_type = selector

    if sel_type not in ALLOWED_LOC_TYPES:
        raise ValueError('Unknown locator type %s' % sel_type)

    wait = WebDriverWait(driver, timeout, poll_frequency, (NoSuchElementException, StaleElementReferenceException))

    if find_single:
        return wait.until(lambda dri: dri.find_element(sel_type, selector))
    else:
        return wait.until(lambda dri: dri.find_elements(sel_type, selector))


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
