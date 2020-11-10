import logging
from xml import parsers
from xml.dom import minidom

import requests

from taf.utils import typeassert
from .api_base_client import APIBaseClient

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RestBaseClient(APIBaseClient):
    @typeassert(rq_body=str, params=dict)
    def send_req(self, method, url, headers, rq_body=None, params=None):
        rq_body = rq_body or ''
        params = params or {}

        logger.info('*********************** REQUEST START ***********************')

        url = url + '?' + '&'.join(
            '%s=%s' % (k, v) for k, v in params.items()) if params else url
        logger.info('%s to <%s>' % (method, url))
        logger.info('Headers: ' + str(headers))

        try:
            reparsed = minidom.parseString(rq_body)
            logger.info('Request Body: \n' + reparsed.toprettyxml(indent="\t"))

        except parsers.expat.ExpatError:
            # request str is in json format
            logger.info('Request Body: \n' + rq_body)

        response = None
        if rq_body:
            response = requests.request(method, url, headers=headers, data=rq_body,
                                        verify=self.verify_ssl)
        if params:
            response = requests.request(method, url, headers=headers, verify=self.verify_ssl)

        logger.info('***********************  REQUEST END  ***********************')

        self.output_response(response)
