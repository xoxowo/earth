import datetime
import json
import math

from django.utils      import timezone
from django.views      import View
from django.http       import JsonResponse
from django.db.models  import Q, Count

from core.emunutils   import StatuesEnum, DayEnum
from core.utils       import calculate_working_time
from detection.models import Detection, State, Area
from equipment.models import Equipment

class EquipmonetListView(View):
    def get(self, request):
        try:
            type      = request.GET.getlist('type', ['excavators', 'backhoe', 'bulldozer', 'wheel_loader'])
            area      = request.GET.getlist('area_id', [1, 2])
            sort_type = request.GET.get('sort_by', 'all')

            sort_options = {
                'all'      : 'serial_number',
                'equipment': 'type__name',
            }

            equipments = Equipment.objects.select_related('type').filter(type__name__in=type, area__id__in=area)

            results = [{
                'equipment_id'     : equipment.id,
                'equipment_type'   : equipment.type.name,
                'serial_number'    : equipment.serial_number,
                'equipment_company': equipment.company,
                'equipment_area'   : equipment.area.name
            }for equipment in equipments.order_by(sort_options[sort_type])]

            return JsonResponse({'message':results}, status=200)
        except ValueError:
            return JsonResponse({'message':'Value_Error'}, status=400)    
        except KeyError:
            return JsonResponse({'message':'Key_Error'}, status=400)

    def post(self, request):
        try:
            data              = json.loads(request.body)
            equipment_type    = data['equipment_type']
            serial_number     = data['serial_number']
            equipment_company = data['equipment_company']
            equipment_area    = data['equipment_area']
            # 1안 : 장비 타입과 구역명은 프론트에서 셀렉트박스로 선택 하는 방식
            Equipment.objects.create(
                type_id       = equipment_type,
                serial_number = serial_number,
                company       = equipment_company,
                area_id       = equipment_area
            )
            # 2안 : 사용자가 직접 장비 타입 ('backhoe')과 구역 명을 입력할 경우 
            # equipment = DetectionType.objects.get(name=equipment_type)
            # area = Area.objects.get(name=equipment_area)
            
            # Equipment.objects.create(
            #     type_id       = equipment.id,
            #     serial_number = serial_number,
            #     company       = equipment_company,
            #     area_id       = area.id
            # )
            return JsonResponse({'message':'Success'}, status=201)
        except ValueError:
            return JsonResponse({'message':'Value_Error'}, status=400)
        except KeyError:
            return JsonResponse({'message':'Key_Error'}, status=400)

class EquipmentDetailView(View):
    def get(self, request, equipment_id):
        try:
            now          = timezone.now()
            weekday      = now.weekday() 
            mon_datetime = now - datetime.timedelta(days=weekday) 
            equipment    = Equipment.objects.get(id=equipment_id)
            rate         = Detection.objects.select_related('equipment_id') \
                            .filter(equipment_id=equipment_id, datetime__date__gte=mon_datetime)

            mon = rate.filter(datetime__iso_week_day=DayEnum.MON.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            tue = rate.filter(datetime__iso_week_day=DayEnum.TUE.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            wed = rate.filter(datetime__iso_week_day=DayEnum.WED.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            thu = rate.filter(datetime__iso_week_day=DayEnum.THU.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            fri = rate.filter(datetime__iso_week_day=DayEnum.FRI.value).exclude(state_id=StatuesEnum.IDEL.value).count()
            sat = rate.filter(datetime__iso_week_day=DayEnum.SAT.value).exclude(state_id=StatuesEnum.IDEL.value).count()

            calculation = lambda x : math.ceil((x*10/28800)*100)

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

    def patch(self, request, equipment_id):
        try:
            data = json.loads(request.body)
            equipment = Equipment.objects.get(id=equipment_id)

            equipment.type_id       = data['equipment_type']
            equipment.serial_number = data['serial_number']
            equipment.company       = data['equipment_company']
            equipment.area_id       = data['equipment_area']

            equipment.save()

            return JsonResponse({'message':'Success'}, status=200)

        except ValueError:
            return JsonResponse({'message':'Value_Error'}, status=400)

        except Equipment.DoesNotExist:
            return JsonResponse({'message':'Invalid_Equipment'}, status=404)

        except KeyError:
            return JsonResponse({'message':'Key_Error'}, status=400)

    def delete(self, request, equipment_id):
        try:
            equipment = Equipment.objects.get(id=equipment_id)

            if not Equipment.objects.filter(id=equipment_id).exists():
                return JsonResponse({'message':'Dose_Not_Exist'}, status = 404)

            equipment.delete()
            return JsonResponse({'message':'No_Content'}, status=204)

        except Equipment.DoesNotExist:
            return JsonResponse({'message':'Invalid_Equipment'}, status=404)

        except KeyError:
            return JsonResponse({'message':'Key_Error'}, status=400)


class AnalysisView(View):
    def get(self, request):       
        try: 
            select  = request.GET['select']

            today = timezone.now()  # 장고 timezon.now는 settings.py 참고해서 local time을 반환 가능

            if select == 'daily' or not select:
                q            = Q(datetime__date=today)
                working_time = calculate_working_time(today, select)

            elif select == 'weekly':
                weekday      = today.isoweekday() # 1:월, 2:화, 3:수, 4:목, 5:금, 6:토, 7:일
                last_sunday  = today - datetime.timedelta(days=weekday)
                q            = Q(datetime__date__gt=last_sunday)
                working_time = calculate_working_time(today, select)
                
            elif select == 'monthly':
                month        = today.month
                q            = Q(datetime__month=month)
                working_time = calculate_working_time(today, select)

            else : 
                return JsonResponse({'message': 'Value_Error'}, status=404)

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
                equip_states = equips_states.filter(serial_number=equip['serial_number'])
                states[equip['serial_number']] = {
                    state.equipment_state : equip_states.get(state=state)['count']*10 \
                                                if equip_states.filter(state=state) \
                                                else 0
                    for state in State.objects.all()
                }    
                result = states[equip['serial_number']]
                utilization_rates[equip['serial_number']] = (result['travel'] + result['load'] + result['unload']) /working_time

        except KeyError:
            return JsonResponse({'message': 'Key_Error'}, status=400)     

        return JsonResponse({'message': 'SUCCESS', 'truck_count': truck_count, 'states': states, 'utilization_rates': utilization_rates},  status=200)

