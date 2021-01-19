# Radio Control

Proceso que ejecuta comandos sobre la tarjeta de radio

# Install

sudo apt-get install python3-dev -y
sudo apt install python3-pip -y

sudo pip3 install paho-mqtt
sudo pip3 install python-dotenv
sudo pip3 install pyinstaller

# Construir Binario

python setup.py install

# Configuración

Variables de ambiente en archivo .env

LOG_LEVEL='debug'
MQTT_HOST=161.35.6.128
MQTT_USER=mosquitouser
MQTT_PASS=mosquitoclave01
MQTT_TOPIC_REQ=/control/radio/request
MQTT_TOPIC_RES=/control/radio/response

# Ejecutar 

hackrf-control lab \
    --verbose \
    --offline \
    --mqtt-host 161.35.6.128 \
    --mqtt-port 18830 \
    --mqtt-user waio \
    --mqtt-pass t3aJFMMyYJuDcCtr \
    --mqtt-topic-req /waio/rpc/request \
    --mqtt-topic-res /waio/rpc/response

