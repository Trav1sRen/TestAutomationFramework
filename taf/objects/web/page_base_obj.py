class PageBaseObject:
    _locators = {}  # container of locators, needs to be overwritten

    def __new__(cls, *args, **kwargs):
        raise TypeError('Cannot directly instantiate the base class <%s>' % cls.__name__)

    def get_loc(self, name):
        """
        Get element locator from container
        :param name: web element name
        :return: locator of web element
        """
        return self._locators[name]
