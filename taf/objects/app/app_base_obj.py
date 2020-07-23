from taf.objects.web import PageBaseObject
from taf.utils.app_utils import ALLOWED_MOBILE_LOC_TYPES


class AppBaseObject(PageBaseObject):
    _allowed_locs = ALLOWED_MOBILE_LOC_TYPES

    def __new__(cls, *args, **kwargs):
        if cls is AppBaseObject:
            raise TypeError('Cannot directly instantiate %s' % cls)
        return object.__new__(cls)
