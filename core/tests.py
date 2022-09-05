from django.test import TestCase, Client

from area.models      import Area
from equipment.models import Equipment
from detection.models import Detection, DetectionType, State

class RealTimeViewTest(TestCase):
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

        type1=DetectionType.objects.create(
            id   = 1,
            name = 'backhoe'
        )
        
        type2=DetectionType.objects.create(
            id   = 2,
            name = 'bulldozer'
        )
        State.objects.create(
            id              = 1,
            equipment_state = 'idle'
        )
        State.objects.create(
            id              = 2,
            equipment_state = 'load'
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
        Detection.objects.create(
            id             = 1,
            x              = 10,
            y              = 200,
            width          = 10,
            height         = 20,
            serial_number  = 'aaa-001',
            area_id        = 1,
            datetime       = '2022-08-30 10:00:00',
            detection_type = type1,
            state_id       = 1,
            equipment_id   = 1
        )
        Detection.objects.create(
            id             = 2,
            x              = 20,
            y              = 300,
            width          = 20,
            height         = 30,
            serial_number  = 'aaa-002',
            area_id        = 1,
            datetime       = '2022-08-30 10:00:00',
            detection_type = type2,
            state_id       = 2,
            equipment_id   = 2
        )

    def tearDown(self):
        Area.objects.all().delete()
        DetectionType.objects.all().delete()
        State.objects.all().delete()
        Equipment.objects.all().delete()
        Detection.objects.all().delete()
    
    def test_realtime_detection_list_view(self):
        client   = Client()
        response = client.get('')

        self.assertEqual(response.json(),
            {
                'message':'Not_Detected',
            }
        )
        self.assertEqual(response.status_code, 400)