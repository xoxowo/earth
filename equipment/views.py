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