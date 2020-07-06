from selenium.webdriver.common.by import By


class PageBaseObject:
    _locators = {}  # container of locators, needs to be overwritten

    def __init__(self):
        if not all(isinstance(obj, dict) for obj in self._locators.values()):
            raise TypeError('Mapping of the element name shall be <dict>')

        if not all(loc in list(By.__dict__.values())[2:-2]
                   for locs in self._locators.values() for loc in locs):
            raise ValueError('Illegal locator type exists in class variable <_locators>')

    def get_loc(self, name, *, loc_type):
        """
        Get element locator from container
        :param name: web element name
        :param loc_type: locator type (recommend to use By class variable)
        :return: locator of web element
        """

        return self._locators[name][loc_type], loc_type
