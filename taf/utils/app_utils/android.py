import os
import re


class AndroidDevices:
    def __init__(self):
        self.udids = []
        for line in os.popen('adb devices').readlines()[1:-1]:
            udid = re.findall(r'^\w*\b', line)[0]
            self.udids.append(udid)

    @property
    def versions(self):
        """ Get the os version of connected devices """

        return list(map(lambda udid: os.popen(
            'adb -s %s shell getprop ro.build.version.release' % udid).readlines()[0].strip('\n'),
                        self.udids))

    @property
    def device_names(self):
        """ Get the product name of connected devices (Sometimes unnecessary) """

        return list(map(lambda udid: os.popen(
            'adb -s %s shell getprop ro.product.model' % udid).readlines()[0].strip('\n'),
                        self.udids))
