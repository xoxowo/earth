import json

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
            for area in Area.objects.all()
            }

            q = Q()            
            if area_id:
                q &= Q(id=area_id)            

            areas = Area.objects.filter(q)

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
        except Exception as e:
            print('예외 발생:', e)

    ## 구역 추가, 수정 기능
    def post(self, request):
        data = json.loads(request.body)
        area_id = request.POST.get('area')

        try: 
            name          = data['name']
            address       = data['address']
            latitude      = data['latitude']
            longitude     = data['longitude']
            cam_latitude  = data['cam_latitude']
            cam_longitude = data['cam_longitude']

            check_list = [latitude, longitude, cam_latitude, cam_longitude]
            for i in check_list:
                int(i)  # 숫자가 아니면 ValueError 발생
                if int(i) < 0:  # 양수가 아니면 경고 문구 출력 후 POST는 진행
                    print('%s is not positive integer!' %i)

            Area.objects.update_or_create(
                id = area_id,
                defaults= {
                    'name'          : name,
                    'address'       : address,
                    'latitude'      : latitude,
                    'longitude'     : longitude,
                    'cam_latitude'  : cam_latitude,
                    'cam_longitude' : cam_longitude
                }
            )
            return JsonResponse({'message': 'SUCCESS'},  status=201)
        except KeyError:
            return JsonResponse({'message': 'Key_Error'},  status=400)
        except ValueError:
            return JsonResponse({'message': 'Value_Error'}, status=400)                    
        except Area.DoesNotExist:
            return JsonResponse({'message': 'ID_Error'}, status=404)      
        except Exception as e:
            print('예외 발생:', e)            

    ## 구역 삭제 기능
    def delete(self, request, area_id):
        try:
            area = Area.objects.get(id=area_id)
            area.delete()

            return JsonResponse({'message': 'SUCCESS'},  status=204)
        except Area.DoesNotExist:
            return JsonResponse({'message': 'Value_Error'}, status=404)
        except Exception as e:
            print('예외 발생:', e)            

class AreaDetailView(View): 
    def get(self, request, area_id):
        try:
            area = Area.objects.get(id=area_id)

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
        except Exception as e:
            print('예외 발생:', e)            

    def patch(self, request, area_id):
        data = json.loads(request.body)

        try: 
            name          = data['name']
            address       = data['address']
            latitude      = data['latitude']
            longitude     = data['longitude']
            cam_latitude  = data['cam_latitude']
            cam_longitude = data['cam_longitude']

            check_list = [latitude, longitude, cam_latitude, cam_longitude]
            for i in check_list:
                int(i)  # 숫자가 아니면 ValueError 발생
                if int(i) < 0:  # 양수가 아니면 경고 문구 출력 후 POST는 진행
                    print('%s is not positive integer!' %i)            

            Area.objects.get(id = area_id).update(
                name          = name,
                address       = address,
                latitude      = latitude,
                longitude     = longitude,
                cam_latitude  = cam_latitude,
                cam_longitude = cam_longitude
            )
        except KeyError:
            return JsonResponse({'message': 'Key_Error'}, status=400)    
        except ValueError:
            return JsonResponse({'message': 'Value_Error'}, status=400)                    
        except Area.DoesNotExist:
            return JsonResponse({'message': 'ID_Error'}, status=404)
        except Exception as e:
            print('예외 발생:', e)            
            