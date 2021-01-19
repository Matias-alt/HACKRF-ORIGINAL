# -*- coding: utf-8 -*

import logging

formatter = logging.Formatter(
    fmt='%(asctime)s.%(msecs).03d %(levelname)s - %(message)s', 
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("radio-control")
logger.addHandler(handler)

handler.setLevel(logging.INFO)
logger.setLevel(logging.INFO)

def setLevel(debug):

    logLevel = logging.DEBUG if debug else logging.INFO

    handler.setLevel(logLevel)
    logger.setLevel(logLevel)