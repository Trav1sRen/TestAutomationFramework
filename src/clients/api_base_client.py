import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import requests

from xml import parsers
from xml.dom import minidom
from src.utils import encoding


class APIBaseClient:
    rs_body = None
    status_code = int()

    def send_req(self, url, headers, rq_body, req_type):
        logger.info('*********************** REQUEST START ***********************')
        logger.info('%s to <%s>' % (req_type, url))
        logger.info('Headers: ' + str(headers))

        reparsed = minidom.parseString(rq_body)
        logger.info('Request Body: \n' + reparsed.toprettyxml(indent="\t"))

        response = requests.post(url, data=rq_body, headers=headers)
        logger.info('***********************  REQUEST END  ***********************')

        self.status_code = response.status_code
        logger.info('Response Status Code: [' + str(response.status_code) + ']')

        try:
            text = response.text.encode(encoding)
            reparsed = minidom.parseString(text)
            logger.info('Response Body: \n' + reparsed.toprettyxml(indent="\t"))
            self.rs_body = text
        except parsers.expat.ExpatError:
            logger.info('Response Body: \n' + response.text)
