from taf.utils import ALLOWED_LOC_TYPES


class PageBaseObject:
    _locators = {}  # container of locators

    _allowed_locs = ALLOWED_LOC_TYPES

    def __new__(cls, *args, **kwargs):
        if cls is PageBaseObject:
            raise TypeError('Cannot directly instantiate %s' % cls)
        return object.__new__(cls)

    def _set_loc(self, name, loc, loc_type):
        """
        Set element locator into container (Please use this method in the __init__() of subclass)
        :param name: web element name
        :param loc: locator expression
        :param loc_type: locator type (recommend to use By class variable)
        """

        if loc_type not in self._allowed_locs:
            raise ValueError('Illegal locator type <%s>' % loc_type)

        self._locators.setdefault(name, {})[loc_type] = loc

    def get_loc(self, name, *, loc_type):
        """
        Get element locator from container
        :param name: web element name
        :param loc_type: locator type (recommend to use By class variable)
        :return: locator of web element
        """

        return self._locators[name][loc_type], loc_type
