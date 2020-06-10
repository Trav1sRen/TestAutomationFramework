import base64
import configparser

import rootpath

proj_root = rootpath.detect()  # this is the project's root path

# retrieve project properties
config = configparser.ConfigParser()
config.read(proj_root + '/properties.ini')

encoding = config['Default']['encoding']


def generate_auth(username, pwd):
    data_bytes = ('%s:%s' % (username, pwd)).encode(encoding)
    return 'Basic ' + base64.b64encode(data_bytes).decode(encoding)
