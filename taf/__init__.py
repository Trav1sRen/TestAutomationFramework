from collections.abc import Sequence, Iterable


def flap_map(func, data, depth=1):
    if depth == 1:
        if not isinstance(data, Sequence):
            raise TypeError('Processed data must be a sequence, not %s' % type(data))

    for d in data:
        if isinstance(d, Sequence):
            depth += 1
            yield from flap_map(func, d, depth=depth)
        else:
            if isinstance(d, Iterable):
                raise TypeError('Iterable subelement could only be sequence')
            else:
                yield func(d)
