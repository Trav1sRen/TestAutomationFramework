from collections.abc import Iterable

from .api_utils import CustomDict
from .api_utils import encoding, var_dict, proj_root
from .api_utils import typeassert, xml2dict, validate_schema
from .web_utils import check_os, _fluent_wait, web_fluent_wait, ALLOWED_LOC_TYPES


def flat_map(seq, func=None):
    if not isinstance(seq, (list, tuple)):
        raise TypeError('Flattened data must be <list> or <tuple>')
    for sub in seq:
        if isinstance(sub, Iterable) and not isinstance(sub, (str, dict)):
            yield from flat_map(sub, func)
        else:
            if func is None:
                yield sub
            else:
                r = func(sub)
                try:
                    yield from flat_map(r)
                except TypeError:
                    yield r
