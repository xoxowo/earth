import paho.mqtt.client as mqtt
import time, ssl, json
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musma_project.settings")
django.setup()

from core.utils import save_data_in_MYSQL

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)

data = None # message로 받아온 데이터를 저장해둘 변수
def on_message(client, userdata, msg):
    global data
    data = json.loads(msg.payload.decode('utf-8'))
    save_data_in_MYSQL(data)

client = mqtt.Client(client_id="") # client_id는 생략 가능
client.on_connect = on_connect
client.on_message = on_message  # subscribe 메세지가 들어오면 작동하는 Method

ca_file, cert_file, key_file = './certification/ca.pem', './certification/cert.pem', './certification/cert-key.pem' 

mqtt_endpoint = 'mqtt-dsmepbs.cauto.musma.net'
client.tls_set(ca_certs=ca_file, certfile=cert_file, keyfile=key_file, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
client.tls_insecure_set(True)

client.connect(mqtt_endpoint, 7001)
time.sleep(5)

client.subscribe('dsmepbs/wecode') # wecode topic subscribe

client.loop_forever()


