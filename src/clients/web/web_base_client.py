import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import re
from collections.abc import Iterable, Sequence

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from src.utils import proj_root, config, check_os, fluent_wait


class WebBaseClient:
    driver = None  # initialized driver

    def init_driver(self, browser, with_proxy=False, headless=False):
        proxy = config['WEB']['proxy']
        os = check_os()

        if browser == 'Chrome':
            exe_path = proj_root + '/drivers/' + os + '/chromedriver.exe'

            chrome_options = webdriver.ChromeOptions()
            if headless:
                chrome_options.add_argument('--headless')
            if with_proxy:
                chrome_options.add_argument('--proxy-server=%s' % proxy)
            chrome_options.add_argument('--window-size=1024,768')
            chrome_options.add_argument('--window-position=0,0')

            self.driver = webdriver.Chrome(executable_path=exe_path, options=chrome_options)

    def nevigate_to(self, url):
        """
        Nevigate to the specific page
        :param url: page url to open
        """

        self.driver.get(url)

    def switch_window(self, index=-1):
        """
        Switch to the window by specified index
        :param index: default is -1, which is the latest opened
        """

        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[index])

    def click_operation(self, locator=None, *, locators=None, sel_type=By.CSS_SELECTOR, double=False, bundle=False):
        """
        Click the web element, double click is optional
        :param locator: element locator
        :param locators: container of element locators. When it is a dict, the value is the selector type
        :param sel_type: locator type
        :param double: flag to decide if double-clicking the element
        :param bundle: flag to decide if bundle of elements to be clicked sequentially
        """

        if bundle:
            if not isinstance(locators, Iterable):
                raise ValueError('"locators" param should be an iterable if "bundle" flag is positive')

            if isinstance(locators, dict):
                for loc, sel in locators.items():
                    self.click_operation(loc, sel_type=sel, double=double)
            else:
                for loc in locators:
                    self.click_operation(loc, double=double)

        element = fluent_wait(self.driver, locator, sel_type)

        if not element.is_selected():
            if not double:
                element.click()
            else:
                action_chains = ActionChains(self.driver)
                action_chains.double_click(element).perform()

    def execute_script(self, script, locator=None, sel_type=By.CSS_SELECTOR, find_single=True, level='document'):
        """
        Execute JavaScript at specified level
        :param script: JavaScript expression
        :param locator: locator of element if level is 'element'
        :param sel_type: locator type
        :param find_single: flag to decide if returning single element other than list of elements
        :param level: level of script executing on
        """

        if level not in ('document', 'element'):
            raise ValueError('Accept a wrong argument for "level"')

        err_msg = 'Script expression has no valid pattern'
        if level == 'element':
            if not re.match(r'arguments\[\d+\]', script):
                raise ValueError(err_msg)
            found = fluent_wait(self.driver, locator, sel_type, find_single)
            self.driver.execute_script(script, found)
        else:
            if not re.match(r'document', script):
                raise ValueError(err_msg)
            self.driver.execute_script(script)

    def select_val(self, locator, sel_type=By.CSS_SELECTOR, *, keyword):
        """
        Select the value on select box by specified keyword
        :param locator: locator of the select box
        :param sel_type: locator type
        :param keyword: keyword of selection, could be int or str
        """

        select = Select(fluent_wait(self.driver, locator, sel_type))

        if isinstance(keyword, int):
            select.select_by_index(keyword)
        else:
            try:
                select.select_by_visible_text(keyword)
            except NoSuchElementException:
                logger.warning('Could not locate element with visible text "%s", try with value attribute' % keyword)
                select.select_by_value(keyword)

    def expect_text_to_be(self, locator=None, *, locators=None, sel_type=By.CSS_SELECTOR, expected_val='',
                          multi_assert=False):
        """
        Compare element text with expectation, comparing multiple texts is supported
        :param locator: element locator
        :param locators: container of element locators. When it is a dict, the value is the selector type
        :param sel_type: locator type
        :param expected_val: expected text value(s), could be a sequence
        :param multi_assert: flag to decide the multiple comparison
        """

        if multi_assert:
            if not (isinstance(locators, Iterable) and isinstance(expected_val, Sequence)):
                raise ValueError(
                    '"locators" and "expected_val" param should be an iterable if "multi_assert" flag is positive')

            if isinstance(locators, dict):
                actual = map(lambda ele: ele.text,
                             (fluent_wait(self.driver, loc, sel) for loc, sel in locators.items()))
            else:
                actual = map(lambda ele: ele.text,
                             (fluent_wait(self.driver, loc, sel_type) for loc in locators))

        else:
            actual = fluent_wait(self.driver, locator, sel_type).text

        logger.info('Actual text value(s): %s' % list(actual))
        logger.info('Expected text value(s): %s' % list(expected_val))
        assert list(actual) == list(expected_val)
