import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CommonDriverOps:
    def __init__(self, driver, wait_fn):
        """ Load initialized web or app driver from subclass """

        self.driver = driver
        self._wait_fn = wait_fn

    def type_text(self, locator, text, sel_type=By.CSS_SELECTOR):
        """ Type text into input box """

        self._wait_fn(self.driver, locator, sel_type=sel_type).send_keys(text)

        # For chain call
        return self

    def click(self, locator, sel_type=By.CSS_SELECTOR, double=False):
        """ Click the element, double click is optional """

        ele = self._wait_fn(self.driver, locator, sel_type=sel_type)

        if not double:
            ele.click()
        else:
            action_chains = ActionChains(self.driver)
            action_chains.double_click(ele).perform()

        return self

    def expect_text_to_contain(self, locator, expect, sel_type=By.CSS_SELECTOR):
        """ Compare element text with expectation """

        actual = self._wait_fn(self.driver, locator, sel_type=sel_type).text
        assert expect in actual

        return self

    def is_ele_exist(self, locator, sel_type=By.CSS_SELECTOR):
        """ Check if element exists, if exists, return this element, return None otherwise """

        try:
            # Hard code timeout here to prevent waiting too long if element does not exist
            return self._wait_fn(self.driver, locator, sel_type=sel_type, timeout=5)
        except TimeoutException:
            return None
