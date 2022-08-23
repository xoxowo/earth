from datetime import datetime, timedelta
from django import views
from pytz     import timezone, utc

from django.http       import JsonResponse
from django.views      import View
from django.db.models  import Q
from django.db.models import Avg, Min, Max, Count, F, Sum

from .models import Detection, State, Equipment

KST = timezone('Asia/Seoul')


class AnalysisView(View):
    def get(self, request):        
        select  = request.GET.get('select')  

        now            = datetime.utcnow()
        today_datetime = utc.localize(now).astimezone(KST)

        q = Q()

        if select == 'daily' or not select:
            q &= Q(datetime__date=today_datetime)
            working_time = 8*60*60

        elif select == 'weekly':
            weekday = today_datetime.weekday() # 0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일
            mon_datetime = today_datetime - timedelta(days=weekday)
            q &= Q(datetime__date__gte=mon_datetime)
            working_time = 5* 8*60*60
            
        elif select == 'monthly':
            month = today_datetime.month 
            q &= Q(datetime__month=month) 
            working_time = 20 * 5 * 8*60*60

        else :
            return JsonResponse({'message': 'Query Parameter Error'}, status=400)

        detection_by_period = Detection.objects.filter(q)  
        print('기간내 데이터:',detection_by_period.count(),'개','\n','쿼리셋:',detection_by_period)

        # truck = detection_by_period.filter(detection_type__name = 'truck').values('serial_number').annotate(count=Count('serial_number'))
        ## 일단은 시리얼 넘버 없으니 state 로 세보자
        truck        = detection_by_period.filter(detection_type__name = 'truck').values('state').annotate(count=Count('state'))
        excavators   = detection_by_period.filter(detection_type__name = 'excavators')
        backhoe      = detection_by_period.filter(detection_type__name = 'backhoe')
        bulldozer    = detection_by_period.filter(detection_type__name = 'bulldozer')
        wheel_loader = detection_by_period.filter(detection_type__name = 'wheel_loader')
 
        truck_count        = truck.count()
        excavators_state   = {state.state : excavators.filter(state__state=state.state).count()*10 for state in State.objects.all()}
        backhoe_state      = {state.state : backhoe.filter(state__state=state.state).count()*10 for state in State.objects.all()}
        bulldozer_state    = {state.state : bulldozer.filter(state__state=state.state).count()*10 for state in State.objects.all()}
        wheel_loader_state = {state.state : wheel_loader.filter(state__state=state.state).count()*10 for state in State.objects.all()}

        excavators_state['utilization_rate']   = (excavators_state['travel'] + excavators_state['load'] + excavators_state['unload']) /working_time
        backhoe_state['utilization_rate']      = (backhoe_state['travel'] + backhoe_state['load'] + backhoe_state['unload']) / working_time
        bulldozer_state['utilization_rate']    = (bulldozer_state['travel'] + bulldozer_state['load'] + bulldozer_state['unload']) / working_time
        wheel_loader_state['utilization_rate'] = (wheel_loader_state['travel'] + wheel_loader_state['load'] + wheel_loader_state['unload']) / working_time

        results = {'truck_count': truck_count, 'excavators_state': excavators_state, 'backhoe_state': backhoe_state, 'bulldozer_state': bulldozer_state, 'wheel_loader_state': wheel_loader_state}


        return JsonResponse({'message': 'SUCCESS', 'results': results},  status=200)
  