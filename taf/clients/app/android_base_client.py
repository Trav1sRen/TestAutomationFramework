import sys

from appium import webdriver

from taf.utils.app_utils import AndroidDevices


class AndroidBaseClient:
    driver = None  # Initialized andriod driver

    desired_caps = {}  # Desired capabilities

    devices = AndroidDevices()  # Instance of connected Android devices

    def init_android_driver(self, apk_name, device_index=0, port=4723, automation_name='UiAutomator2', auto_grant=True):
        self.desired_caps['platformName'] = 'Android'
        self.desired_caps['platformVersion'] = self.devices.versions[device_index]
        self.desired_caps['udid'] = self.devices.udids[device_index]
        self.desired_caps['app'] = sys.path[1] + '/apk/%s.apk' % apk_name

        if auto_grant is True:
            self.desired_caps['autoGrantPermissions'] = auto_grant

        if automation_name != 'UiAutomator2':
            self.desired_caps['automationName'] = automation_name

        self.driver = webdriver.Remote('http://localhost:%s/wd/hub' % port, self.desired_caps)

    def update_desired_caps(self, **kwargs):
        """ Use this function to add special caps """
        for key, val in kwargs.items():
            self.desired_caps[key] = val
