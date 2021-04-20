import logging
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import Select

from taf.clients import CommonDriverOps
from taf.utils import proj_root, check_os, web_fluent_wait

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebBaseClient(CommonDriverOps):
    def __init__(self, *args, **kwargs):
        """ Initialize the web driver """

        self.driver = self._init_web_driver(*args, **kwargs)

        super(WebBaseClient, self).__init__(self.driver, web_fluent_wait)

    @staticmethod
    def _init_web_driver(browser, by_proxy='', headless=False, accept_untrusted_certs=True,
                         window_width=1440,
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
        :return initialized web driver
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

            return webdriver.Chrome(executable_path=exe_path, options=chrome_options)

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

            return webdriver.Firefox(executable_path=exe_path, options=ff_options)

    def nevigate_to(self, url):
        """
        Nevigate to the specific page
        :param url: page url to open
        """

        self.driver.get(url)

    def scroll_to(self, x=0, y='document.body.scrollHeight', to_bottom=False,
                  scroll_pause_time=0.5):
        """
        Scroll to specified coordinate
        :param x: horizontal ordinate
        :param y: vertical ordinate
        :param to_bottom: flag to decide if to scroll to the bottom of a page with infinite loading
        :param scroll_pause_time: pause time of infinite scroll until reach the bottom
        """

        if not to_bottom:
            self.driver.execute_script('window.scrollTo(%s, %s)' % (x, y))
        else:
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                self.scroll_to()

                # Wait to load page
                time.sleep(scroll_pause_time)

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
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
                logger.warning(
                    'Could not locate element with visible text "%s", try with value attribute' % keyword)
                select.select_by_value(keyword)
