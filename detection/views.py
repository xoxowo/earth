import datetime
import calendar 

from django.http       import JsonResponse
from django.utils      import timezone
from django.views      import View

from detection.models import Detection
from area.models      import Area
from core.utils       import DayEnum


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

# KST = timezone('Asia/Seoul')

class ProgressView(View):
    def get(self, request):
        select = request.GET.get('select')

        # now            = datetime.utcnow()
        # today_datetime = utc.localize(now).astimezone(KST)
        today = datetime.date.today()

        progress_detection = Detection.objects.filter(serial_number='wheel_loader-000')

        if select == 'realtime':
            results = {
                area.name : progress_detection.filter(area_id=area.id).last().progress\
                                if progress_detection.filter(area_id=area.id) else 0
                for area in Area.objects.all()[:2]
            }
        else:
            if select == 'weekly':
                weekday  = today.weekday() # 0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일
                mon_datetime = today - datetime.timedelta(days=weekday)
                dates    = [mon_datetime + datetime.timedelta(days=Weekday.value) for Weekday in DayEnum]

            elif select == 'monthly':
                last_date = calendar.monthrange(today.year,today.month)[1]
                dates = [today.replace(day=date) for date in range(1, last_date+1)]
            else:
                return JsonResponse({'message': 'Query Parameter Error'}, status=400)
            
            results = {}
            for area in Area.objects.all()[:2]:
                results[area.name] = []
                for date in dates:

                    if date.weekday() == DayEnum.SUN.value: 
                        date1 = date-datetime.timedelta(days=1)
                    else :
                        date1 = date

                    progress_date_area    = progress_detection.filter(datetime__date=date1, area=area)

                    results[area.name].append({
                    'day'     : date.day,
                    'progress': progress_date_area.last().progress\
                                    if  progress_date_area\
                                    else '없음'
                    })

        return JsonResponse({'message': 'SUCCESS', 'results': results}, status=200)
