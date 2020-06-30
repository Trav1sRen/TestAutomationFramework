import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from xml import parsers
from xml.dom import minidom
from .api_base_client import APIBaseClient
from taf.utils import typeassert


class RestBaseClient(APIBaseClient):
    @typeassert(rq_body=str, params=(type(None), dict))
    def send_req(self, method, url, headers, rq_body=None, params=None):
        if not self.verify_ssl:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        if not (rq_body or params is not None):
            raise ValueError('You must at least pass the post body or query params when sending the restful request')

        if rq_body and params:
            raise ValueError('You cannot specify the post body and query params together')

        logger.info('*********************** REQUEST START ***********************')

        if params is not None:  # may be an empty {}
            url = url + '?' + '&'.join('%s=%s' % (k, v) for k, v in params.items())
        logger.info('%s to <%s>' % (method, url))
        logger.info('Headers: ' + str(headers))

        try:
            reparsed = minidom.parseString(rq_body)
            logger.info('Request Body: \n' + reparsed.toprettyxml(indent="\t"))

        except parsers.expat.ExpatError:
            # request str is in json format
            logger.info('Request Body: \n' + rq_body)

        if params is not None:
            response = requests.request(method, url, headers=headers, verify=self.verify_ssl)
        else:
            response = requests.request(method, url, headers=headers, data=rq_body, verify=self.verify_ssl)
        logger.info('***********************  REQUEST END  ***********************')

        self.status_code = response.status_code
        logger.info('Response Status Code: [' + str(response.status_code) + ']')
        text = response.text

        try:
            reparsed = minidom.parseString(text)
            logger.info('Response Body: \n' + reparsed.toprettyxml(indent="\t"))

        except parsers.expat.ExpatError:
            # response str is in json or other format
            logger.info('Response Body: \n' + text)

        self.rs_body = text
