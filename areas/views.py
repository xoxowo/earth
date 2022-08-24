from pytz     import timezone, utc

from django.http       import JsonResponse
from django.views      import View
from django.db.models  import Q


from .models import Area

KST = timezone('Asia/Seoul')

class AreaListView(View):
    def get(self, request):
        # 구역 리스트 반환
        # 구역 이름으로 검색 -> id로 주세욤
        # 구역 이름, 위도, 경도, 카메라 위도, 카메라 경도

        area_id = request.GET.get('area')

        area_list = {
            area.id : area.name
        for area in Area.objects.all()
        }

        q = Q()
        
        if area_id:
            q &= Q(id=area_id)            

        areas = Area.objects.filter(q)

        if not areas:
            return JsonResponse({'message': 'Area ID Error'},  status=404)

        results = [{
            'area_id' : area.id,
            'area_name' : area.name,
            'address' : area.address,
            'latitude' : area.latitude,
            'longitude' : area.longitude,
            'cam_latitude' : area.cam_latitude,
        }
        for area in areas]

        return JsonResponse({'message': 'SUCCESS', 'area_list': area_list ,'results': results},  status=200)
