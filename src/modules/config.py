# -*- coding: utf-8 -*

from .logger import logger

import json
import os

homedir = os.path.join(os.getenv("HOME"), '.hackrf-control')
filename = os.path.join(homedir, 'config.json')

##
#

def read_config():

    if not os.path.isdir(homedir):
        os.makedirs(homedir)

    if os.path.isfile(filename):
        logger.debug("opening %s", filename)
        with open(filename, "r") as fd:
            data = json.load(fd)

    else:
        logger.debug("creating %s", filename)
        data = {
            "samplerate" : 1000000,
            "gain"       : 15,
            "frecuency"  : 490000000,
            "carrier"    : 1000,
            "waveform"   : "constant",
            "_waveform"  : False
        }
        with open(filename, "w") as fd:
            json.dump(data, fd)

    return data

##
#

def save_config(data):

    logger.debug("updating data config [%s]", data)

    with open(filename, "r+") as fd:
        db = json.load(fd)
        logger.debug("data old [%s]", db)
        for key in data:
            if key in db:
                db[key] = data[key]

    with open(filename, "w") as fd:
        logger.debug("data new [%s]", db)
        json.dump(db, fd)