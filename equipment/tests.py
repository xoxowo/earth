import json

from django.test import TestCase, Client

from area.models      import Area
from detection.models import DetectionType
from equipment.models import Equipment

class EquipmonetViewTest(TestCase):
    def setUp(self):
        client = Client()

        Area.objects.create(
            id            = 1,
            name          = '구역A',
            address       = '충주시 부여군',
            latitude      = 123.11111,
            longitude     = 123.11111,
            cam_latitude  = 333.33333,
            cam_longitude = 333.11111
        )

        type1 = DetectionType.objects.create(
            id   = 1,
            name = 'backhoe'
        )
        
        type2 = DetectionType.objects.create(
            id   = 2,
            name = 'bulldozer'
        )

        Equipment.objects.create(
            id            = 1,
            company       = 'aaa',
            serial_number = 'aaa-1',
            type          = type1,
            area_id       = 1
        )
        Equipment.objects.create(
            id            = 2,
            company       = 'aaa',
            serial_number = 'aaa-2',
            type          = type2,
            area_id       = 1
        )

    def tearDown(self):
        Area.objects.all().delete()
        DetectionType.objects.all().delete()
        Equipment.objects.all().delete()

    def test_equipment_list(self):
        client   = Client()
        response = client.get('/equipment/list')

        self.assertEqual(response.json(),
            {
                'message':[
                    {
                        'equipment_id'     : 1,
                        'equipment_type'   : 'backhoe',
                        'serial_number'    : 'aaa-1',
                        'equipment_company': 'aaa',
                        'equipment_area'   : '구역A'
                    },
                    {
                        'equipment_id'     : 2,
                        'equipment_type'   : 'bulldozer',
                        'serial_number'    : 'aaa-2',
                        'equipment_company': 'aaa',
                        'equipment_area'   : '구역A'
                    },
                ],
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_equipments_post_view(self):
        client   = Client()
        equipment = {
            'equipment_type'   : 1,
            'serial_number'    : 'aaa-3',
            'equipment_company': 'aaa',
            'equipment_area'   : 1
        }
        response = client.post('/equipment/list', json.dumps(equipment), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {
                'message':'Success'
            }
        )

    def test_fail_equipments_post_view(self):
        client   = Client()
        equipment = {
            'equipment_typee'   : 1,
            'serial_number'    : 'aaa-3',
            'equipment_company': 'aaa',
            'equipment_area'   : 1
        }
        response = client.post('/equipment/list', json.dumps(equipment), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                'message':'Key_Error'
            }
        )

    def test_equipments_detail_view(self): 
        client   = Client()
        response = client.get('/equipment/1')

        self.assertEqual(response.json(),
            {
                'message':{
                    'equipment_type': 'backhoe',
                    'serial_number' : 'aaa-1',
                    'company'       : 'aaa',
                    'equipment_area': '구역A'
                },
                'availablete_rating': [
                    {'date': '월', 'rate': 0},
                    {'date': '화', 'rate': 0},
                    {'date': '수', 'rate': 0},
                    {'date': '목', 'rate': 0},
                    {'date': '금', 'rate': 0},
                    {'date': '토', 'rate': 0},]
                },
        )
        self.assertEqual(response.status_code, 200)