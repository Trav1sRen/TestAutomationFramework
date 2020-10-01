import logging
from xml.dom import minidom

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from taf.utils import typeassert
from .api_base_client import APIBaseClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SoapBaseClient(APIBaseClient):
    @typeassert(rq_body=str)
    def send_req(self, url, headers, rq_body):
        if not self.verify_ssl:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        logger.info('*********************** REQUEST START ***********************')
        logger.info('%s to <%s>' % ('POST', url))
        logger.info('Headers: ' + str(headers))

        reparsed = minidom.parseString(rq_body)
        logger.info('Request Body: \n' + reparsed.toprettyxml(indent="\t"))

        response = requests.request('POST', url, headers=headers, data=rq_body, verify=self.verify_ssl)
        logger.info('***********************  REQUEST END  ***********************')

        self.output_response(response)
