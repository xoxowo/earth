import datetime

from django.http       import JsonResponse
from django.utils      import timezone
from django.views      import View

from detection.models import Detection

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