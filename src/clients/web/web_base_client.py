import re
from collections.abc import Iterable

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

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

    def click_operation(self, locator=None, *, locators=None, sel_type='css', double=False, bundle=False):
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
                raise ValueError('"locators" param should be an iterable if "bundle" flag is positive')

            if isinstance(locators, dict):
                for loc, sel in locators.items():
                    self.click_operation(loc, sel_type=sel, double=double)
            else:
                for loc in locators:
                    self.click_operation(loc, double=double)

        element = fluent_wait(self.driver, locator, sel_type)
        if not double:
            element.click()
        else:
            action_chains = ActionChains(self.driver)
            action_chains.double_click(element).perform()

    def execute_script(self, script, locator=None, sel_type='css', find_single=True, level='document'):
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