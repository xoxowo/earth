import datetime
import calendar 

from django.http      import JsonResponse
from django.utils     import timezone
from django.views     import View
from django.db.models import Q

from core.utils       import PROGRESS_DETECTION
from core.emunutils   import DayEnum
from detection.models import Detection
from area.models      import Area


class RealTimeView(View):
    def get(self, request):
        try:
            detection_options = Detection.objects.filter(datetime__gte = timezone.now() - datetime.timedelta(seconds=10))
            real_time         = detection_options.first()

            if real_time == None :
                return JsonResponse({'message':'Not_Detected'}, status=400)
            
            results = [{
                'datetime'  : real_time.datetime,
                'type' : [{ 
                    'detection_info': detection_option.detection_type.name,
                    'state'         : detection_option.state.equipment_state,
                    } for detection_option in detection_options]
            }]
            
            return JsonResponse({'message':results}, status=200)

        except KeyError:
            JsonResponse({'message':'Key_Error'}, status=400)


class ProgressView(View):
    def get(self, request):
        try:
            select  = request.GET.get('select')
            area_name = request.GET.get('area_name')

            today = timezone.now() 

            progress_detection = Detection.objects.filter(serial_number=PROGRESS_DETECTION)

            q = Q()
            if area_name:
                q &= Q(name=area_name)

            if select == 'realtime':
                results =[]
                for area in Area.objects.all():
                    results.append({
                        'name' : area.name,
                        'progress' : progress_detection.filter(area_id=area.id).last().progress\
                                        if progress_detection.filter(area_id=area.id) \
                                        else '없음'
                    })

            else:
                if select == 'weekly':
                    weekday     = today.isoweekday() # 1:월, 2:화, 3:수, 4:목, 5:금, 6:토, 7:일
                    last_sunday = today - datetime.timedelta(days=weekday)
                    dates       = [last_sunday + datetime.timedelta(days=Weekday.value) for Weekday in DayEnum]

                elif select == 'monthly':
                    last_date = calendar.monthrange(today.year,today.month)[1]
                    dates = [today.replace(day=date) for date in range(1, last_date+1)]
                else:
                    return JsonResponse({'message': 'Value_Error'}, status=404)
                
                areas = Area.objects.filter(q)
                if not areas:
                    return JsonResponse({'message': 'Value_Error'}, status=404)

                results = {}
                for area in areas:
                    results[area.name] = []
                    for date in dates:

                        if date.isoweekday() == DayEnum.SUN.value: 
                            progress_date = date-datetime.timedelta(days=1)
                        else :
                            progress_date = date

                        progress_date_area    = progress_detection.filter(datetime__date=progress_date, area=area)

                        results[area.name].append({
                            'day'     : date.day,
                            'progress': progress_date_area.last().progress\
                                            if  progress_date_area\
                                            else '없음'
                        })

            return JsonResponse({'message': 'SUCCESS', 'results': results}, status=200)

        except Exception as e:
            print('예외 발생:', e)