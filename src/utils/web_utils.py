from platform import system

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait

from .common_utils import config


def fluent_wait(driver, selector, sel_type='css', find_single=True, timeout=config['WEB']['wait_timeout'],
                poll_frequency=config['WEB']['poll_frequency']):
    wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency,
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
    if system() == 'Linux':
        return 'linux'
    elif system() == "Darwin":
        return 'mac'
    elif system() == "Windows":
        return 'win'

