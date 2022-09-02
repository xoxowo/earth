from django.http       import JsonResponse
from django.views      import View
from django.db.models  import Q

from .models           import Area

class AreaListView(View):
    def get(self, request):
        try:
            area_id = request.GET.get('area')

            area_list = {
                area.id : area.name
            for area in Area.objects.all()[:2]
            }

            q = Q()
            
            if area_id:
                q &= Q(id=area_id)            

            areas = Area.objects.filter(q)[:2]

            if not areas:
                return JsonResponse({'message': 'Value_Error'},  status=404)

            results = [{
                'area_id'      : area.id,
                'area_name'    : area.name,
                'address'      : area.address,
                'latitude'     : area.latitude,
                'longitude'    : area.longitude,
                'cam_latitude' : area.cam_latitude,
                'cam_longitude': area.cam_longitude,
            }
            for area in areas]

            return JsonResponse({'message': 'SUCCESS', 'area_list': area_list ,'results': results},  status=200)
        except KeyError:
            return JsonResponse({'message': 'Key_Error'}, status=400)   

class AreaDetailView(View): 
    def get(self, request, area_name):
        try:
            area = Area.objects.get(name=area_name)

            results = {
                'area_id'      : area.id,
                'area_name'    : area.name,
                'address'      : area.address,
                'latitude'     : area.latitude,
                'longitude'    : area.longitude,
                'cam_latitude' : area.cam_latitude,
                'cam_longitude': area.cam_longitude,
            }

            return JsonResponse({'message': 'SUCCESS', 'results': results},  status=200)
        except Area.DoesNotExist:
            return JsonResponse({'message': 'Value_Error'}, status=404)