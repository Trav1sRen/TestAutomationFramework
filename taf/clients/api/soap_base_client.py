import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from xml import parsers
from xml.dom import minidom
from .api_base_client import APIBaseClient
from taf.utils import typeassert


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

        self.status_code = response.status_code
        logger.info('Response Status Code: [' + str(response.status_code) + ']')
        text = response.text

        try:
            reparsed = minidom.parseString(text)
            logger.info('Response Body: \n' + reparsed.toprettyxml(indent="\t"))

        except parsers.expat.ExpatError:
            logger.info('Response Body: \n' + text)

        self.rs_body = text