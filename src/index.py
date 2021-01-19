#!/usr/bin/python
# -*- coding: utf-8 -*

from modules import logger
from modules import setLevel
from modules import subscribe
from modules import read_config
from modules import save_config

from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta

import subprocess
import argparse
import signal
import time
import glob
import sys
import os
import re

##
#

def signal_handle(signum, frame):
    logger.info("sigterm received (%d)", signum)
    sys.exit(0)

##
#

def main():

    signal.signal(signal.SIGINT,  signal_handle)
    signal.signal(signal.SIGTERM, signal_handle)

    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--mqtt-host")
    parser.add_argument("--mqtt-port")
    parser.add_argument("--mqtt-user")
    parser.add_argument("--mqtt-pass")
    parser.add_argument("--mqtt-topic-req")
    parser.add_argument("--mqtt-topic-res")

    args = parser.parse_args()
    name = args.name

    load_dotenv()

    log_level = os.getenv("LOG_LEVEL", "info").lower()
    setLevel(args.verbose or log_level == 'debug')

    mqtt_host = args.mqtt_host or os.getenv("MQTT_HOST")
    mqtt_port = args.mqtt_port or os.getenv("MQTT_PORT")
    mqtt_user = args.mqtt_user or os.getenv("MQTT_USER")
    mqtt_pass = args.mqtt_pass or os.getenv("MQTT_PASS")

    mqtt_topic_req = args.mqtt_topic_req or os.getenv('MQTT_TOPIC_REQ')
    mqtt_topic_res = args.mqtt_topic_res or os.getenv('MQTT_TOPIC_RES')

    topic_req = f"{mqtt_topic_req}/{name}"
    topic_res = f"{mqtt_topic_res}/{name}"
    
    logger.debug("Starting MQTT")

    nextConnectionAt = datetime.now()
    connected = False

    HOME = os.getenv("HOME")

    pattern = re.compile(r'^Modify: (.*)\n')

    while True:

        now = datetime.now()

        if not connected and now > nextConnectionAt:
            try:
                
                @subscribe(topic_req, {"host": mqtt_host, "port": int(mqtt_port), "user": mqtt_user, "pass": mqtt_pass})
                def message_handle(payload, emit):
                    
                    try:
                        if 'id' not in payload:
                            raise Exception("request id is not present")
                            
                        if 'command' not in payload:
                            raise Exception("command is not present")

                        command = payload['command']

                        if command == 'status':
                            settings = read_config()
                            logger.info("settings: [%s]", settings)

                            found = glob.glob(f"{HOME}/.pm2/pids/hackrf-control-*")
                            status = 'stopped'
                            uptime = None

                            if found:
                                status = 'online'

                                with open(found[0]) as fd:
                                    pid = fd.read()

                                out = subprocess.check_output(f"stat /proc/{pid} | grep Modify", shell=True, encoding="utf-8")
                                res = pattern.findall(out)

                                uptime = res[0] if res else None

                            emit(topic_res, {
                                'id': payload['id'], 
                                'settings': settings,
                                'process': {
                                    'status': status,
                                    'uptime': uptime
                                }
                            })

                        elif command == 'logs':

                            lines = payload.get('lines', 10)
                            out = subprocess.check_output(f"tail {HOME}/.pm2/logs/hackrf-control-error.log -n {lines}", shell=True, encoding="utf-8")
                            
                            data = []

                            for x in out.split('\n'):
                                
                                created_at = x[0:23]

                                pos = x.find(" ", 24)
                                level = x[23:pos]

                                pos = x.find(" ", pos+1)
                                content = x[pos:]

                                data.append({'created_at': created_at, 'level': level, 'content': content})

                            emit(topic_res, {
                                'id': payload['id'], 
                                'data': data
                            })

                        elif command == 'config':

                            if 'settings' not in payload:
                                raise Exception("settings is not present")
                            
                            settings = payload['settings']
                            settings['_waveform'] = 'waveform' in settings

                            logger.info("settings: [%s]", settings)
                            save_config(settings)

                            emit(topic_res, {'id': payload['id']})

                        else:
                            emit(topic_res, {'id': payload['id']})
                   
                    except Exception as ex:
                        logger.warning("%s", payload)
                        logger.error(ex)

                        emit(topic_res, {'id': payload['id'], 'error': ex})

                logger.info("mqtt connected")
                connected = True

            except Exception as ex:
                logger.error(ex)

                connected = False
                nextConnectionAt = now + timedelta(seconds=10)

                logger.debug("Reconnecting mqtt at 10 seconds")

        time.sleep(0.1)
##
#

if __name__ == '__main__':
    main()
