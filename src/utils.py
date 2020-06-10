import configparser

import rootpath

proj_root = rootpath.detect()  # this is the project's root path

# retrieve project properties
config = configparser.ConfigParser()
config.read(proj_root + '/properties.ini')

encoding = config['Default']['encoding']
