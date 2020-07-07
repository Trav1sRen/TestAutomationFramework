class APIBaseClient:
    rs_body = ''  # response str

    status_code = int()  # response status code

    verify_ssl = False  # control whether we verify the server's TLS certificate

    def __new__(cls, *args, **kwargs):
        if cls is APIBaseClient:
            raise TypeError('Cannot directly instantiate the base class %s' % cls)
        return object.__new__(cls)
