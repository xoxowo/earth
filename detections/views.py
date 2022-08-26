from django.http       import JsonResponse
from django.views      import View
from django.db.models  import Q
from django.db.models  import Count

from detections.models import Detection
from areas.models      import Area

class ProgressView(View):
    def get(self, request):
        ## 실시간, 주간 일별, 월간 일별 공정률 - 모두 구역별로!
        ## query parameter로 select = realtime, weekly, monthly 받아오기
        ## Detection table에서 특정장비(wheel_loader-000 으로 가정)의 데이터만 가져오기
        ## realtime 이면 해당 장비의 데이터 중 last 데이터를 가져오고 그 데이터의 progress 값을 반환
        ## weekly 면 이번주 월~일요일 날짜에 해당하는 데이터들을 가져와서 각 날짜의 마지막 데이터의 progress를 날짜와 함께 반환
        ## monthly 면 이번달에 해당하는 데이터들을 가져와서 각 날짜의 마지막 데이터의 progress를 날짜와 함께 반환
        select = request.GET.get('select')

        progress_detection = Detection.objects.filter(serial_number='wheel_loader-000')

        if select == 'realtime':
            results = {
                area.name : progress_detection.filter(area_id=area.id).last().progress if progress_detection.filter(area_id=area.id) else 0
                for area in Area.objects.all()
            }
        else:
            if select == 'weekly':
                q = Q()
            elif select == 'monthly':
                q = Q()
            else:
                return JsonResponse({'message': 'Query Parameter Error'}, status=400)

            progress_detection_by_period = progress_detection.filter(q)
            dates = progress_detection_by_period.values('datetime__date').annotate(Count('datetime__date'))

            results = {
                area.name : {
                    date['datetime__date'].day :  progress_detection_by_period.filter(datetime__date=date['datetime__date'], area=area).last().progress if  progress_detection_by_period.filter(datetime__date=date['datetime__date'], area=area) else '없음'
                    for date in dates
                }                
                for area in Area.objects.all()
            }
            
        return JsonResponse({'message': 'SUCCESS', 'results': results}, status=200)
