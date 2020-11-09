from ..clients.api import SoapBaseClient
from ..utils import typeassert


class ApiEntrance:
    def __init__(self, module_name, cls_name, *args, **kwargs):
        module = __import__('src.objects.api.' + module_name, fromlist=[''])  # 'fromlist' arg is not an empty list
        self.api_obj = getattr(module, cls_name)(*args, **kwargs)

    @typeassert(extra_headers=dict)
    def dispatch_soap_request(self, verify_ssl=False, extra_headers=None, **xml_args):
        self.api_obj.construct_xml(soap=True, **xml_args)

        extra_headers = extra_headers or {}
        if extra_headers:
            self.api_obj.append_headers(extra_headers)

        client = SoapBaseClient(verify_ssl=verify_ssl)
        client.send_req(self.api_obj.url, self.api_obj.default_headers, self.api_obj.rq_body)

        self.api_obj.load_client_response(client.rs_body)
        self.api_obj.process_response()
