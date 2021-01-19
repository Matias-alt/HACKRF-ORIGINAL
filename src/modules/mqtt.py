# -*- coding: utf-8 -*

from .logger import logger

import paho.mqtt.client as mqtt
import json

topics = []

def on_connect(client, userdata, level, buf):
    logger.debug("on_connect: %s", buf)

    for topic in topics:
        logger.debug("subscribing to %s", topic)
        client.subscribe(topic)

def on_log(client, userdata, level, buf):
    logger.debug("on_log: %s", buf)

def on_publish(client, userdata, mid):
    logger.debug("on_publish: ok")

def subscribe(topic, auth):

    topics.append(topic)

    logger.debug("AUTH: %s", auth)

    def decorator(handle):

        try:

            client = mqtt.Client()
            client.username_pw_set(auth['user'], auth['pass'])
            client.connect(auth['host'], auth['port'])
            client.on_log = on_log
            client.on_publish = on_publish
            client.on_connect = on_connect

            def emit(topic, data):
                publishing = True 
                res = client.publish(topic, json.dumps(data))
                logger.debug("publish response: %s", res)

            def on_message(client, userdata, message):
                payload = str(message.payload, 'utf-8')
                logger.debug("received: [%s] %s", message.topic, payload)
                handle(json.loads(payload), emit)

            client.on_message = on_message
            #client.subscribe(topic)

            client.loop_start()

        except Exception as ex:
            logger.error(ex)
            raise ex

    return decorator

