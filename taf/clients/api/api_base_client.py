import logging
from functools import partial
from xml import parsers
from xml.dom import minidom

from taf.utils import cannot_be_instantiated

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class APIBaseClient:
    rs_body = ''  # response str

    status_code = int()  # response status code

    verify_ssl = False  # control whether we verify the server's TLS certificate

    __new__ = partial(cannot_be_instantiated, name='APIBaseClient')

    def output_response(self, response):
        self.status_code = response.status_code
        logger.info('Response Status Code: [' + str(response.status_code) + ']')
        text = response.text

        try:
            # response is in xml format
            reparsed = minidom.parseString(text)
            logger.info('Response Body: \n' + reparsed.toprettyxml(indent="\t"))

        except parsers.expat.ExpatError:
            logger.info('Response Body: \n' + text)

        self.rs_body = text
