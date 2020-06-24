from taf import NotInstantiated


class APIBaseClient(metaclass=NotInstantiated):
    rs_body = ''
    status_code = int()

    verify_ssl = False  # control whether we verify the server's TLS certificate
