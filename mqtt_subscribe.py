
from pytz import timezone
import paho.mqtt.client as mqtt
import time, ssl, json, re

import mysql.connector
import my_db_settings

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musma_project.settings")
django.setup()

from detections.models import Detection

KST = timezone('Asia/Seoul')

# ./my_db_settings.py
mydb = my_db_settings.mydb

mycursor = mydb.cursor()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)

# previous_x = 0

def on_message(client, userdata, msg):
    # print(msg.payload)
    # print(msg.payload.decode('utf-8'))
    # 여기에 데이터 수신 시 해야할 job을 작성하세요.
    data = json.loads(msg.payload.decode('utf-8'))

    cam_id                 = data['cam_id']
    detection_count        = data['detection_count']
    datetime               = data['datetime']   # "2022-08-18T11:45:41+0900"
    detection_informations = data['detection_information']
      
    # YYYY-MM-DD hh:mm:ss 형태로 변형 필요  ## fromisoformat은 형태가 약간 안 맞음 ㅠㅠ
    datetime_split = re.split('[T|+]',datetime)   # T 랑 + 기준으로 한번에 split 하는 방법!
    datetime1 = datetime_split[0] + ' ' + datetime_split[1]

    for i in range(detection_count):
        detection_information = detection_informations[i]

        detection_type = detection_information['detection_type']
        serial_number  = detection_information['id']
        x              = detection_information['x']
        y              = detection_information['y']
        width          = detection_information['width']
        height         = detection_information['height']
        state          = detection_information['state']     
 
        # detection_type1 = DetectionType.objects.get(name = detection_type) 이걸 SQL문으로..
        mycursor.execute('SELECT id FROM detection_types WHERE name=%s', (detection_type,))
        detection_type1, = mycursor.fetchone()  
        # print(detection_type1)  # fetchone()해서 찍어보니 (1,)로 나와서 detection_type뒤에 , 찍어서 값만 할당!

        # state1 = State.objects.get(name = state)
        mycursor.execute('SELECT id FROM states WHERE equipment_state=%s', (state,))
        state1, = mycursor.fetchone()
        # print(state1)

        if detection_type == 'truck':
            equipment1 = None
        else :
            mycursor.execute('SELECT id FROM equipments WHERE serial_number=%s',(serial_number,))
            equipment1, = mycursor.fetchone()

        if serial_number == 'wheel_loader-000':   # 이걸로 가정
            last = Detection.objects.filter(serial_number==serial_number).last()

            last_x        = last.x        if last else 0
            last_progress = last.progress if last else 0

            if last_x < x <= 200 :    ## 음... 200에 멈춰있으면..... last_x = x 이므로 false!!
                progress = last_progress//10 + x/200*10
            else: 
                progress = last_progress
        else :
            progress = None

        sql = '''INSERT 
            INTO detections (x,y,width,height,serial_number,datetime,area_id,detection_type_id,state_id, equipment_id, progress) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        val = (x,y,width,height,serial_number,datetime1,cam_id, detection_type1, state1, equipment1, progress)
        mycursor.execute(sql,val)

        mydb.commit() # commit을 해줘야 DB에 실제로 입력이 됨

        # ### 알별 공정률 저장하기     
        # global previous_x
        # if serial_number == 'wheel_loader-000':
        #     if datetime_split[1] > '18:00:00':
        #         # laps = Detection.objects.filter(serial_number=serial_number, x=200).count()
        #         # if previous_x < x < 200:
        #         #     progress = laps*0.10 + x/200*0.10
        #         # elif 200 < x :
        #         #     아니면 미리 200보다 큰 x는 200으로 저장해버릴까...
        #         # elif x < previous_x :
        #         #     progress = laps*0.10 

        #         previous_progress = Progress.objects.last().progress # 전날 작업 마감시 공정률

        #         if previous_x < x :   
        #             progress = previous_progress // 10 + int(x/200 *10)
        #         elif x < previous_x :
        #             progress = previous_progress // 10 + 10

        #         sql = '''INSERT 
        #             INTO progresses (progress, date, area_id) 
        #             VALUES (%s, %s, %s)
        #             '''
        #         val = (progress, datetime1,cam_id)
        #         mycursor.execute(sql,val)        

        #         mydb.commit()     

        #     if x != previous_x:
        #         previous_x = x
           
    print('%s %s개의 데이터를 저장했습니다.' % (datetime1, detection_count))

client = mqtt.Client(client_id="wecode-melony2222") # client_id는 생략 가능
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

    
