from selenium import webdriver

from src.utils import proj_root, config, check_os


class WebBaseClient:
    driver = None

    def __init__(self, browser):
        self.browser = browser

    def init_driver(self, with_proxy=False, headless=False):
        proxy = config['WEB']['proxy']
        os = check_os()

        if self.browser == 'Chrome':
            exe_path = proj_root + '/drivers/' + os + '/chromedriver.exe'

            chrome_options = webdriver.ChromeOptions()
            if headless:
                chrome_options.add_argument('--headless')
            if with_proxy:
                chrome_options.add_argument('--proxy-server=%s' % proxy)
            chrome_options.add_argument('--window-size=1024,768')
            chrome_options.add_argument('--window-position=0,0')

            self.driver = webdriver.Chrome(executable_path=exe_path, options=chrome_options)
