from src import NotInstantiated


class APIBaseClient(metaclass=NotInstantiated):
    rs_body = ''
    status_code = int()
