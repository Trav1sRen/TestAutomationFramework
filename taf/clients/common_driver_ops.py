import logging
from collections.abc import Sequence

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from taf.utils import web_fluent_wait, UNSUPPORTED_TYPE, fluent_wait

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CommonDriverOps:
    def __init__(self, driver):
        """ Load initialized web or app driver from subclass """

        self.driver = driver

    def type_text(self, locator, text, sel_type=By.CSS_SELECTOR):
        """ Type text into input box """

        web_fluent_wait(self.driver, locator, sel_type=sel_type).send_keys(text)

        # For chain call
        return self

    def click(self, locator, sel_type=By.CSS_SELECTOR, double=False):
        """ Click the element, double click is optional """

        ele = web_fluent_wait(self.driver, locator, sel_type=sel_type)

        if not double:
            ele.click()
        else:
            action_chains = ActionChains(self.driver)
            action_chains.double_click(ele).perform()

        return self

    def expect_text_to_be(self, locator=None, *, locators=None, sel_type=By.CSS_SELECTOR,
                          expected_val,
                          multi_assert=False):
        """ Compare element text with expectation, comparing multiple texts is supported """

        if multi_assert:
            if isinstance(locators, dict):
                actual = [web_fluent_wait(self.driver, loc, sel_type=sel).text for loc, sel in
                          locators.items()]
            elif isinstance(locators, (tuple, list)):
                actual = [web_fluent_wait(self.driver, loc, sel_type=sel_type).text for loc in
                          locators]
            else:
                raise TypeError(UNSUPPORTED_TYPE % (type(locators), 'locators'))

        else:
            actual = web_fluent_wait(self.driver, locator, sel_type=sel_type).text

        logger.info('Actual text value(s): %s' % list(actual))
        logger.info('Expected text value(s): %s' % list(expected_val))
        assert list(actual) == list(expected_val)

    def if_element_exists(self, locator, sel_type=By.CSS_SELECTOR):
        """ Check if element exists, if exists, return this element, return None otherwise """

        try:
            # Hard code timeout here to prevent waiting too long if element does not exist
            return fluent_wait(self.driver, locator, sel_type=sel_type, timeout=5)
        except TimeoutException:
            return None
