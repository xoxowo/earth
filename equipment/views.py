import datetime
import json

from django.utils import timezone
from django.views import View
from django.http  import JsonResponse

from core.emunutils   import StatuesEnum, DayEnum
from detection.models import Detection
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