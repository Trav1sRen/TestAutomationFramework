from functools import partial

from taf.utils import cannot_be_instantiated


class APIBaseClient:
    rs_body = ''  # response str

    status_code = int()  # response status code

    verify_ssl = False  # control whether we verify the server's TLS certificate

    __new__ = partial(cannot_be_instantiated, name='APIBaseClient')
