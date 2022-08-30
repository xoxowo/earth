import datetime
import calendar 

from django.http       import JsonResponse
from django.utils      import timezone
from django.views      import View

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
                dates    = [today - datetime.timedelta(days=weekday-i) for i in range(7)]

            elif select == 'monthly':
                dates = [today.replace(day=i) for i in range(1, calendar.monthrange(today.year,today.month)[1]+1)]
            else:
                return JsonResponse({'message': 'Query Parameter Error'}, status=400)
            
            results = []
            for i in range(len(dates)) :
                results.append({'day': dates[i].day})

                for area in Area.objects.all()[:2]:
                    if dates[i].weekday() == 6:  # 일요일은 토요일 공정률과 동일한 값으로
                        date1 = dates[i]-datetime.timedelta(days=1)
                    else :
                        date1 = dates[i]

                    progress_date_area    = progress_detection.filter(datetime__date=date1, area=area)
                    results[i][area.name] = progress_date_area.last().progress\
                                                if  progress_date_area\
                                                else '없음'

        return JsonResponse({'message': 'SUCCESS', 'results': results}, status=200)
