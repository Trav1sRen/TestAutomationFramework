import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from xml import parsers

import requests
from xml.dom import minidom
from src.utils import encoding


class APIBaseClient:
    rs_body = None

    def __init__(self, req_type):
        self.status_code = int()
        self.req_type = req_type

    def send_req(self, url, headers, rq_body):
        logger.info('*********************** REQUEST START ***********************')
        logger.info('Request to <' + url + '>')
        logger.info('Headers: ' + str(headers))

        reparsed = minidom.parseString(rq_body)
        logger.info('Request Body: \n' + reparsed.toprettyxml(indent="\t"))

        response = requests.post(url, data=rq_body, headers=headers)
        logger.info('***********************  REQUEST END  ***********************')
        self.status_code = response.status_code
        logger.info('Response Status Code: [' + str(response.status_code) + ']')

        try:
            reparsed = minidom.parseString(response.text)
            logger.info('Response Body: \n' + reparsed.toprettyxml(indent="\t"))
            self.rs_body = bytes(response.text, encoding=encoding)
        except parsers.expat.ExpatError:
            logger.info('Response Body: \n' + response.text)
