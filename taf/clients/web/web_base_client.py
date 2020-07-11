import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import re
import sys
import time
from datetime import datetime
from collections.abc import Iterable, Sequence

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.proxy import Proxy, ProxyType

from taf.utils import proj_root, check_os, web_fluent_wait


class WebBaseClient:
    driver = None  # initialized driver

    def init_driver(self, browser, by_proxy='', headless=False, accept_untrusted_certs=True, window_width=1440,
                    window_height=900, window_maximized=False):
        """
        Initialize the web driver for various browser type
        :param browser: browser type
        :param by_proxy: If testing by proxy
        :param headless: If activating headless mode
        :param accept_untrusted_certs: If accepting untrusted certs of website
        :param window_width: width of initialized driver window
        :param window_height: height of initialized driver window
        :param window_maximized: If maximizing the driver window
        """

        os = check_os()
        if browser == 'Chrome':
            exe_path = proj_root + '/drivers/%s/chromedriver%s' % os
            chrome_options = webdriver.ChromeOptions()

            if headless:
                chrome_options.add_argument('--headless')
            if by_proxy:
                chrome_options.add_argument('--proxy-server=%s' % by_proxy)
            if accept_untrusted_certs:
                chrome_options.add_argument('--ignore-certificate-errors')
            if not window_maximized:
                chrome_options.add_argument('--window-size=%s,%s' % (window_width, window_height))
                chrome_options.add_argument('--window-position=0,0')
            else:
                chrome_options.add_argument('--start-maximized')

            self.driver = webdriver.Chrome(executable_path=exe_path, options=chrome_options)

        if browser == 'Firefox':
            exe_path = proj_root + '/drivers/%s/geckodriver%s' % os
            ff_options = webdriver.FirefoxOptions()

            if headless:
                ff_options.headless = True
            if by_proxy:
                proxy = Proxy()
                proxy.proxy_type = ProxyType.MANUAL
                proxy.http_proxy = by_proxy
                proxy.socks_proxy = by_proxy
                proxy.ssl_proxy = by_proxy
                ff_options.proxy = proxy
            if accept_untrusted_certs:
                ff_options.accept_insecure_certs = True
            if not window_maximized:
                ff_options.add_argument('--window-size=%s,%s' % (window_width, window_height))
                ff_options.add_argument('--window-position=0,0')
            else:
                ff_options.add_argument('--start-maximized')

            self.driver = webdriver.Firefox(executable_path=exe_path, options=ff_options)

    def nevigate_to(self, url):
        """
        Nevigate to the specific page
        :param url: page url to open
        """

        self.driver.get(url)

    def scroll_to(self, x=0, y='document.body.scrollHeight', to_bottom=False, scroll_pause_time=0.5):
        """
        Scroll to specified coordinate
        :param x: horizontal ordinate
        :param y: vertical ordinate
        :param to_bottom: flag to decide if to scroll to the bottom of a page with infinite loading
        :param scroll_pause_time: pause time of infinite scroll until reach the bottom
        """

        if not to_bottom:
            self.execute_script('window.scrollTo(%s, %s)' % (x, y))
        else:
            last_height = self.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                self.scroll_to()

                # Wait to load page
                time.sleep(scroll_pause_time)

                # Calculate new scroll height and compare with last scroll height
                new_height = self.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

    def take_screenshot(self):
        """
        Should be put in tear_down function of test
        """

        if sys.exc_info()[0]:
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.driver.get_screenshot_as_file(proj_root + '/screenshots/screenshot-%s.png' % now)

    def switch_window(self, index=-1):
        """
        Switch to the window by specified index
        :param index: default is -1, which is the latest opened
        """

        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[index])

    def input_action(self, locator=None, *, locators=None, sel_type=By.CSS_SELECTOR, val, bundle=False):
        """
        Send value(s) to input box(es)
        :param locator: element locator
        :param locators: container of element locators
        :param sel_type: locator type
        :param val: input value(s), could be a sequence
        :param bundle: flag to decide if bundle of values to be sent sequentially
        """

        if bundle:
            if not (isinstance(locators, Iterable) and isinstance(val, Sequence)):
                raise ValueError(
                    'Parameter <locators> and <val> should iterable if <bundle> flag is positive')

            try:
                for i, (loc, sel) in enumerate(dict(locators).items()):
                    self.input_action(loc, sel_type=sel, val=val[i])
            except TypeError:
                for i, loc in enumerate(locators):
                    self.input_action(loc, sel_type=sel_type, val=val[i])
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
            if not isinstance(locators, Iterable):
                raise ValueError('Parameter <locators> should be an iterable if <bundle> flag is positive')

            try:
                for loc, sel in dict(locators).items():
                    self.click_action(loc, sel_type=sel, double=double)
            except TypeError:
                for loc in locators:
                    self.click_action(loc, sel_type=sel_type, double=double)
        else:
            element = web_fluent_wait(self.driver, locator, sel_type=sel_type)

            if not element.is_selected():
                if not double:
                    element.click()
                else:
                    action_chains = ActionChains(self.driver)
                    action_chains.double_click(element).perform()

    def execute_script(self, script, locator=None, sel_type=By.CSS_SELECTOR, find_single=True, level='document',
                       lines=False):
        """
        Execute JavaScript at specified level
        :param script: JavaScript expression
        :param locator: locator of element if level is 'element'
        :param sel_type: locator type
        :param find_single: flag to decide if returning single element other than list of elements
        :param level: level of script executing on
        :param lines: flag to decide if executing lines of script on document level
        """

        if level not in ('document', 'element'):
            raise ValueError('Accept a wrong argument for <level>')

        err_msg = 'Script expression has no valid pattern'
        if level == 'element':
            if not re.match(r'arguments\[\d+\]', script):
                raise ValueError(err_msg)
            found = web_fluent_wait(self.driver, locator, sel_type=sel_type, find_single=find_single)
            self.driver.execute_script(script, found)
        else:
            if lines:
                if not isinstance(script, Sequence):
                    raise ValueError('Parameter <script> should be a sequence if <lines> flag is positive')

                for line in script:
                    self.execute_script(line)

            if not re.match(r'document|window', script):
                raise ValueError(err_msg)
            self.driver.execute_script(script)

    def select_val(self, locator, sel_type=By.CSS_SELECTOR, *, keyword):
        """
        Select the value on select box by specified keyword
        :param locator: locator of the select box
        :param sel_type: locator type
        :param keyword: keyword of selection, could be int or str
        """

        select = Select(web_fluent_wait(self.driver, locator, sel_type=sel_type))

        if isinstance(keyword, int):
            select.select_by_index(keyword)
        else:
            try:
                select.select_by_visible_text(keyword)
            except NoSuchElementException:
                logger.warning('Could not locate element with visible text "%s", try with value attribute' % keyword)
                select.select_by_value(keyword)

    def expect_text_to_be(self, locator=None, *, locators=None, sel_type=By.CSS_SELECTOR, expected_val,
                          multi_assert=False):
        """
        Compare element text with expectation, comparing multiple texts is supported
        :param locator: element locator
        :param locators: container of element locators
        :param sel_type: locator type
        :param expected_val: expected text value(s), could be a sequence
        :param multi_assert: flag to decide the multiple comparison
        """

        if multi_assert:
            if not (isinstance(locators, Iterable) and isinstance(expected_val, Sequence)):
                raise ValueError(
                    'Parameter <locators> and <expected_val> should be iterable if <multi_assert> flag is positive')

            try:
                actual = map(lambda ele: ele.text,
                             (web_fluent_wait(self.driver, loc, sel_type=sel) for loc, sel in dict(locators).items()))
            except TypeError:
                actual = map(lambda ele: ele.text,
                             (web_fluent_wait(self.driver, loc, sel_type=sel_type) for loc in locators))

        else:
            actual = web_fluent_wait(self.driver, locator, sel_type=sel_type).text

        logger.info('Actual text value(s): %s' % list(actual))
        logger.info('Expected text value(s): %s' % list(expected_val))
        assert list(actual) == list(expected_val)
