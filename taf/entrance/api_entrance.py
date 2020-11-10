import json

from ..clients.api import SoapBaseClient, RestBaseClient
from ..utils import typeassert, validate_schema


class ApiEntrance:
    def __init__(self, module_name, cls_name, *args, **kwargs):
        """
        Constructor of class ApiEntrance
        :param module_name: name of the module in which APIBaseObject's subclass located
        :param cls_name: name of the APIBaseObject's subclass
        :param args: Signatures to match the APIBaseObject's subclass's own constructor
        :param kwargs: Signatures to match the APIBaseObject's subclass's own constructor
        """

        module = __import__('src.objects.api.' + module_name,
                            fromlist=[''])  # 'fromlist' arg is not an empty list
        self.api_obj = getattr(module, cls_name)(*args, **kwargs)

    @typeassert(dict, schema_name=str, extra_headers=dict)
    def dispatch_soap_request(self, json_mapping, *, verify_ssl=False, check_schema=False,
                              schema_name=None,
                              extra_headers=None,
                              **xml_args):
        """
        Entrance to dispatch soap request
        :param json_mapping: mapping of json file name and obj name
        :param verify_ssl: flag of if verifying ssl, default is False
        :param check_schema: flag of if checking XML schema
        :param schema_name: name of schema file for reference
        :param extra_headers: extra headers for the request
        :param xml_args: arguments used to construct SOAP body
        """

        self.api_obj.unpack_json(json_mapping).construct_xml(soap=True, **xml_args)

        extra_headers = extra_headers or {}
        if extra_headers:
            self.api_obj.append_headers(extra_headers)

        client = SoapBaseClient(verify_ssl=verify_ssl)
        client.send_req(self.api_obj.url, self.api_obj.default_headers, self.api_obj.rq_body)

        if check_schema:
            schema_name = schema_name or ''
            if schema_name == '':
                raise ValueError('schema name cannot be an empty string')
            validate_schema(client.rs_body, schema_name)

        self.api_obj.load_client_response(client.rs_body).process_response()

    @typeassert(json_mapping=dict, extra_headers=dict)
    def dispatch_rest_request(self, method, json_mapping, *, xml_format=False, verify_ssl=False,
                              extra_headers=None,
                              with_query=None,
                              with_body=None):

        """
        Entrance to dispatch rest request
        :param method: API method to dispatch the request
        :param json_mapping: mapping of json file name and obj name
        :param xml_format: flag of if the request body is in XML format, default is False
        :param verify_ssl: flag of if verifying ssl, default is False
        :param extra_headers: extra headers for the request
        :param with_query: flag of if the request is with query params in the url
        :param with_body: flag of if the request is with request body
        """

        with_query = with_query or False
        with_body = with_body or False

        if not (with_query or with_body):
            raise ValueError('Flag "with_query" and "with_body" cannot all be negative')

        if with_query and with_body:
            raise ValueError('Cannot specify to dispatch with body and query params together')

        self.api_obj.unpack_json(json_mapping)

        if xml_format:
            self.api_obj.construct_xml()  # construct request with XML format
        else:
            self.api_obj.unflatten_json()  # construct request with JSON format

        extra_headers = extra_headers or {}
        if extra_headers:
            self.api_obj.append_headers(extra_headers)

        client = RestBaseClient(verify_ssl=verify_ssl)

        if with_query:
            client.send_req(method, self.api_obj.url, self.api_obj.default_headers,
                            params=self.api_obj.rq_dict)
        if with_body:
            client.send_req(method, self.api_obj.url, self.api_obj.default_headers,
                            # 'indent' arg for pretty print
                            rq_body=json.dumps(self.api_obj.rq_dict, indent=4))

        self.api_obj.load_client_response(client.rs_body).process_response()
