import sys

from appium import webdriver

from taf.clients import CommonDriverOps
from taf.utils.app_utils import AndroidDevices


class AndroidBaseClient(CommonDriverOps):
    def __init__(self, *args, **kwargs):
        """ Initialize the Android driver """

        self.devices = AndroidDevices()  # Instance of connected Android devices

        self.driver = self._init_android_driver(*args, **kwargs)

        super(AndroidBaseClient, self).__init__(self.driver)

    def _init_android_driver(self, apk_name, device_index=0, port=4723,
                             automation_name='UiAutomator2', auto_grant=True,
                             **extra_caps):

        desired_caps = {'platformName': 'Android',
                        'platformVersion': self.devices.versions[device_index],
                        'udid': self.devices.udids[device_index],
                        'app': sys.path[1] + '/apk/%s.apk' % apk_name
                        }  # Desired capabilities

        if auto_grant is True:
            desired_caps['autoGrantPermissions'] = auto_grant

        if automation_name != 'UiAutomator2':
            desired_caps['automationName'] = automation_name

        if extra_caps:
            desired_caps.update(extra_caps)  # inject new caps if needed

        return webdriver.Remote('http://localhost:%s/wd/hub' % port, desired_caps)

    def switch_to_context(self, webview=True):
        """ Switch to the webview or back to native view """

        contexts = self.driver.contexts

        if len(contexts) == 1:
            raise RuntimeError(
                '"WebView.setWebContentsDebuggingEnabled(true)" is not set in app source code')

        if webview:
            self.driver.switch_to.context(
                list(filter(lambda con: con.startswith('WEBVIEW_'), contexts))[0])
        else:
            self.driver.switch_to.context(
                list(filter(lambda con: con == 'NATIVE_APP', contexts))[0])
