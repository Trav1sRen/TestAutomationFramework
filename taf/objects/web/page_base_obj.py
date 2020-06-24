from taf import NotInstantiated


class PageBaseObject(metaclass=NotInstantiated):
    _locators = {}  # container of locators, needs to be overwritten

    def get_loc(self, name):
        """
        Get element locator from container
        :param name: web element name
        :return: locator of web element
        """
        return self._locators[name]
