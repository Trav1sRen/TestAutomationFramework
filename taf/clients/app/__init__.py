import os
import socket
from time import sleep

from .android_base_client import AndroidBaseClient


class AppiumServer:
    def __init__(self, host='127.0.0.1', port=4723):
        self.host = host
        self.port = port

    def is_port_used(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.host, self.port))
            return True
        except OSError:
            return False
        finally:
            s.close()

    def start_appium_service(self):
        while self.is_port_used():
            self.port = self.port + 1

        os.system('appium -a %s -p %d &' % (self.host, self.port))
        sleep(1)

    def stop_appium_service(self):
        res = os.popen('lsof -i tcp:%d' % self.port)
        lines = [line for line in res.read().split('\n') if line != '']

        idx = lines[0].split().index('PID')
        os.system('kill -9 %s' % lines[-1].split()[idx])
