class APIBaseClient:
    rs_body = ''
    status_code = int()

    verify_ssl = False  # control whether we verify the server's TLS certificate

    def __new__(cls, *args, **kwargs):
        raise TypeError('Cannot directly instantiate the base class <%s>' % cls.__name__)
