import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from collections.abc import Sequence

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from taf.utils import web_fluent_wait, UNSUPPORTED_TYPE, cannot_be_instantiated
from functools import partial


class CommonDriverOps:
    __new__ = partial(cannot_be_instantiated, name='CommonDriverOps')

    def __init__(self, driver):
        """ Load initialized web or app driver from subclass """

        self.driver = driver

    def input_action(self, locator=None, *, locators=None, sel_type=By.CSS_SELECTOR, val, bundle=False):
        """
        Send value(s) to input box(es)
        :param locator: element locator
        :param locators: container of element locators
        :param sel_type: locator type
        :param val: input value(s), could be a tuple or list
        :param bundle: flag to decide if bundle of values to be sent sequentially
        """

        if not isinstance(val, Sequence):
            raise TypeError(UNSUPPORTED_TYPE % (type(val), 'val'))

        if bundle:
            if isinstance(val, str):
                raise TypeError(UNSUPPORTED_TYPE % (type(val), 'val'))

            if isinstance(locators, dict):
                for i, (loc, sel) in enumerate(locators.items()):
                    self.input_action(loc, sel_type=sel, val=val[i])
            elif isinstance(locators, (tuple, list)):
                for i, loc in enumerate(locators):
                    self.input_action(loc, sel_type=sel_type, val=val[i])
            else:
                raise TypeError(UNSUPPORTED_TYPE % (type(locators), 'locators'))

        else:
            web_fluent_wait(self.driver, locator, sel_type=sel_type).send_keys(val)

    def click_action(self, locator=None, *, locators=None, sel_type=By.CSS_SELECTOR, double=False, bundle=False):
        """
        Click the web element, double click is optional
        :param locator: element locator
        :param locators: container of element locators
        :param sel_type: locator type
        :param double: flag to decide if double-clicking the element
        :param bundle: flag to decide if bundle of elements to be clicked sequentially
        """

        if bundle:
            if isinstance(locators, dict):
                for loc, sel in locators.items():
                    self.click_action(loc, sel_type=sel, double=double)
            elif isinstance(locators, (tuple, list)):
                for loc in locators:
                    self.click_action(loc, sel_type=sel_type, double=double)
            else:
                raise TypeError(UNSUPPORTED_TYPE % (type(locators), 'locators'))

        else:
            element = web_fluent_wait(self.driver, locator, sel_type=sel_type)

            if not element.is_selected():
                if not double:
                    element.click()
                else:
                    action_chains = ActionChains(self.driver)
                    action_chains.double_click(element).perform()

    def expect_text_to_be(self, locator=None, *, locators=None, sel_type=By.CSS_SELECTOR, expected_val,
                          multi_assert=False):
        """
        Compare element text with expectation, comparing multiple texts is supported
        :param locator: element locator
        :param locators: container of element locators
        :param sel_type: locator type
        :param expected_val: expected text value(s), could be a tuple or list
        :param multi_assert: flag to decide the multiple comparison
        """

        if multi_assert:
            if isinstance(locators, dict):
                actual = [web_fluent_wait(self.driver, loc, sel_type=sel).text for loc, sel in locators.items()]
            elif isinstance(locators, (tuple, list)):
                actual = [web_fluent_wait(self.driver, loc, sel_type=sel_type).text for loc in locators]
            else:
                raise TypeError(UNSUPPORTED_TYPE % (type(locators), 'locators'))

        else:
            actual = web_fluent_wait(self.driver, locator, sel_type=sel_type).text

        logger.info('Actual text value(s): %s' % list(actual))
        logger.info('Expected text value(s): %s' % list(expected_val))
        assert list(actual) == list(expected_val)
