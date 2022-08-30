import datetime
import json
import random

from django.utils import timezone
from django.views import View
from django.http  import JsonResponse
from django.db.models  import Q, Count

from core.emunutils   import StatuesEnum, DayEnum
from detection.models import Detection, State, Area
from equipment.models import Equipment

class EquipmonetListView(View):
    def get(self, request):
        try:
            type      = request.GET.getlist('type', ['excavators', 'backhoe', 'bulldozer', 'wheel_loader'])
            area      = request.GET.getlist('area', ['구역A', '구역B'])
            sort_type = request.GET.get('sort_by', 'all')

            sort_options = {
                'all'           : 'serial_number',
                'equipment'     : 'type__name',
                'owner'         : 'owner_id',
            }

            equipments = Equipment.objects.select_related('type').filter(type__name__in=type, area__name__in=area)

            results = [{
                'equipment_id'     : equipment.id,
                'equipment_type'   : equipment.type.name,
                'serial_number'    : equipment.serial_number,
                'equipment_company': equipment.company,
                'equipment_area'   : equipment.area.name
            }for equipment in equipments.order_by(sort_options[sort_type])]

            return JsonResponse({'message':results}, status=200)

        except KeyError:
            return JsonResponse({'message':'Key_Error'}, status=400)

    def post(self, request):
        try:
            data              = json.loads(request.body)
            equipment_type    = data['equipment_type']
            serial_number     = data['serial_number']
            equipment_company = data['equipment_company']
            equipment_area    = data['equipment_area']

            Equipment.objects.create(
                type_id       = equipment_type,
                serial_number = serial_number,
                company       = equipment_company,
                area_id       = equipment_area
            )
            return JsonResponse({'message':'Success'}, status=200)

        except KeyError:
            return JsonResponse({'message':'Key_Error'}, status=400)

class EquipmentDetailView(View):
    def get(self, request, equipment_id):
        try:
            now          = timezone.now()
            weekday      = now.weekday() 
            mon_datetime = now - datetime.timedelta(days=weekday) 
            equipment    = Equipment.objects.get(id=equipment_id)
            rate         = Detection.objects.select_related('equipment_id').filter(equipment_id=equipment_id, datetime__date__gte=mon_datetime)

            mon = rate.filter(datetime__iso_week_day=DayEnum.MON.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            tue = rate.filter(datetime__iso_week_day=DayEnum.TUE.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            wed = rate.filter(datetime__iso_week_day=DayEnum.WED.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            thu = rate.filter(datetime__iso_week_day=DayEnum.THU.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            fri = rate.filter(datetime__iso_week_day=DayEnum.FRI.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            sat = rate.filter(datetime__iso_week_day=DayEnum.SAT.value).exclude(state_id=StatuesEnum.IDEL.value).count()

            calculation = lambda x : round((x*10/28800)*100)

            results= { 
                'equipment_type' : equipment.type.name,
                'serial_number'  : equipment.serial_number,
                'company'        : equipment.company,
                'equipment_area' : equipment.area.name,
            }
  
            availablete_rating = [
                {
                    'date': '월',
                    'rate': calculation(mon)},
                {
                    'date': '화',
                    'rate': calculation(tue)},
                {
                    'date': '수',
                    'rate': calculation(wed)},
                {
                    'date': '목',
                    'rate': calculation(thu)},
                {
                    'date': '금',
                    'rate': calculation(fri)},
                {
                    'date': '토',
                    'rate': calculation(sat)},
            ]

            return JsonResponse({'message':results,'availablete_rating':availablete_rating}, status=200)

        except Equipment.DoesNotExist:
            return JsonResponse({'message':'Invalid_Equipment'}, status=404)

        except KeyError:
            return JsonResponse({'message':'Key_Error'}, status=400)

# KST = timezone('Asia/Seoul')

class AnalysisView(View):
    def get(self, request):        
        select  = request.GET.get('select')  

        # now            = datetime.utcnow()
        # today_datetime = utc.localize(now).astimezone(KST)
        today = datetime.date.today()

        if select == 'daily' or not select:
            q            = Q(datetime__date=today)
            working_time = 8*60*60

        elif select == 'weekly':
            weekday      = today.weekday() # 0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일
            mon_datetime = today - datetime.timedelta(days=weekday)
            q            = Q(datetime__date__gte=mon_datetime)
            working_time = 5* 8*60*60
            
        elif select == 'monthly':
            month        = today.month
            q            = Q(datetime__month=month)
            working_time = 20 * 5 * 8*60*60

        else :
            return JsonResponse({'message': 'Query Parameter Error'}, status=400)

        detection_by_period = Detection.objects.filter(q).values('serial_number','area','state')

        truck         = detection_by_period.filter(detection_type__name = 'truck').\
                            values('area','serial_number').distinct()
        equips_states = detection_by_period.exclude(detection_type__name = 'truck').\
                            values('serial_number', 'state').\
                                annotate(count=Count('state'))

        truck_count = []
        for area in Area.objects.all():
            truck_count.append({
                'area_name' : area.name ,
                'count' : truck.filter(area=area).count() 
            })
           
        states = {}
        utilization_rates = {}
        
        for equip in Equipment.objects.values('serial_number'):
            serial_name = equip['serial_number'].split('-')[0] + equip['serial_number'].split('-')[1][-1:]
            equip_states = equips_states.filter(serial_number=equip['serial_number'])

            states[serial_name] = {}
            for state in State.objects.all():
                try :
                    states[serial_name][state.equipment_state] = equip_states.get(state=state)['count']*10
                except Detection.DoesNotExist:
                    states[serial_name][state.equipment_state] = 0

            result = states[serial_name]
            utilization_rates[serial_name] = (result['travel'] + result['load'] + result['unload']) /working_time
 
        
        ##################### 더미 데이터 테스트용 #######################

        # dummy = random.randrange(2,5)
        dummy = 4
        serial_name_list = ['excavators1', 'backhoe2', 'bulldozer1', 'wheel_loader6']

        states = {
            i : states[i]
            for i in serial_name_list[:dummy]
        }
        utilization_rates = {
            i : utilization_rates[i]
            for i in serial_name_list[:dummy]
        }

        ##############################################################        

        return JsonResponse({'message': 'SUCCESS', 'truck_count': truck_count, 'states': states, 'utilization_rates': utilization_rates},  status=200)
