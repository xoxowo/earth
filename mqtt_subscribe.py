import paho.mqtt.client as mqtt
import time, ssl, json, re

import mysql.connector
import my_settings

import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musma_project.settings")
django.setup()

from pytz              import timezone

from detection.models import Detection

KST = timezone('Asia/Seoul')

# ./my_db_settings.py
mydb     = my_settings.mydb
mycursor = mydb.cursor()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode('utf-8'))

    cam_id                 = data['cam_id']
    detection_count        = data['detection_count']
    datetime               = data['datetime']   # "2022-08-18T11:45:41+0900"
    detection_informations = data['detection_information']
      
    # YYYY-MM-DD hh:mm:ss 형태로 변형 필요  ## fromisoformat은 형태가 약간 안 맞음 ㅠㅠ
    datetime_split = re.split('[T|+]',datetime)   # T 랑 + 기준으로 한번에 split 하는 방법!
    datetime1      = datetime_split[0] + ' ' + datetime_split[1]

    for i in range(detection_count):
        detection_information = detection_informations[i]

        detection_type = detection_information['detection_type']
        serial_number  = detection_information['id']
        x              = detection_information['x']
        y              = detection_information['y']
        width          = detection_information['width']
        height         = detection_information['height']
        state          = detection_information['state']     
 
        # detection_type1 = DetectionType.objects.get(name = detection_type) 이걸 SQL문으로..!
        mycursor.execute('SELECT id FROM detection_types WHERE name=%s', (detection_type,))
        detection_type1, = mycursor.fetchone()  
        # print(detection_type1)  # fetchone()해서 찍어보니 (1,)로 나와서 detection_type뒤에 ,찍어서 값만 할당!

        # state1 = State.objects.get(name = state)
        mycursor.execute('SELECT id FROM states WHERE equipment_state=%s', (state,))
        state1, = mycursor.fetchone()
        # print(state1)
        print(serial_number, end=', ')
        if detection_type == 'truck':
            equipment1 = None
        else :
            mycursor.execute('SELECT id FROM equipment WHERE serial_number=%s',(serial_number,))
            equipment1, = mycursor.fetchone()

        PROGRESS_DETECTION = 'wheel_loader_000' # 이걸로 가정
        START_POINT = 0  # 시작 x좌표는 0으로 가정
        TURNING_POINT = 2000  # 도착 x좌표는 2000으로 가정

        if serial_number == PROGRESS_DETECTION:  
            last          = Detection.objects.filter(serial_number=serial_number).last()
            last_x        = last.x        if last else START_POINT
            last_progress = last.progress if last and last.progress else 0

            if last_x < x <= TURNING_POINT :    # 음... 2000에 멈춰있으면..... last_x = x 이므로 false!!
                progress = last_progress//10 *10 + x/TURNING_POINT*10
            else: 
                progress = last_progress
        else :
            progress = None

        sql = '''INSERT 
            INTO detection (x,y,width,height,serial_number,datetime,area_id,detection_type_id,state_id, equipment_id, progress) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        val = (x,y,width,height,serial_number,datetime1,cam_id, detection_type1, state1, equipment1, progress)
        mycursor.execute(sql,val)

        mydb.commit() # commit을 해줘야 DB에 실제로 입력이 됨
           
    print('\n >>> %s %s개의 데이터를 저장했습니다.' % (datetime1, detection_count))

client = mqtt.Client(client_id="") # client_id는 생략 가능
client.on_connect = on_connect
client.on_message = on_message  # subscribe 메세지가 들어오면 작동하는 Method

ca_file, cert_file, key_file = './certification/ca.pem', './certification/cert.pem', './certification/cert-key.pem' # 같이 드린 파일

mqtt_endpoint = 'mqtt-dsmepbs.cauto.musma.net'
client.tls_set(ca_certs=ca_file, certfile=cert_file, keyfile=key_file, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
client.tls_insecure_set(True)

client.loop_start()
client.connect(mqtt_endpoint, 7001)
time.sleep(5)

client.subscribe('dsmepbs/wecode') # wecode topic subscribe
while True:
    a = 1

# client.loop_forever()

