from pytz     import timezone, utc

from django.http       import JsonResponse
from django.views      import View
from django.db.models  import Q


from .models import Area

KST = timezone('Asia/Seoul')

class AreaDetailView(View):
    def get(self, request):
        # 특정 구역 정보 
        # 구역 이름, 위도, 경도, 카메라 위도, 카메라 경도, 주 단위로 일간 공정률 

        area_id = request.GET.get('area')

        if not area_id:
            return JsonResponse({'message': 'No Query Parameter'}, status=400)

        try: 
            area = Area.objects.get(id=area_id)
        except Area.DoesNotExist:
            return JsonResponse({'message': 'Area ID Error'}, status=404)

        results = {
            'area_id' : area.id,
            'area_name' : area.name,
            'address' : area.address,
            'latitude' : area.latitude,
            'longitude' : area.longitude,
            'cam_latitude' : area.cam_latitude,
            'cam_longitude' : area.cam_longitude
        }


        return JsonResponse({'message': 'SUCCESS', 'results': results},  status=200)
