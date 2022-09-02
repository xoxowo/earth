import calendar
import datetime
import pandas
from pytimekr import pytimekr

from core.emunutils import DayEnum

WEEKDAY_WORKING_TIME  = 8 * 60 * 60 # 초 단위
SATURDAY_WORKING_TIME = 4 * 60 * 60 # 초 단위
RED_DAY_WORKING_TIME  = 0 

red_days = lambda year : pytimekr.holidays(year) 

def calculate_working_time(today, select):
    if select == 'daily':
        dates = [today]     

    elif select == 'weekly':
        weekday     = today.weekday() # 0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일
        last_monday = today - datetime.timedelta(days=weekday)
        dates       = pandas.date_range(last_monday, periods=7)

    elif select == 'monthly':
        end_day = calendar.monthrange(today.year,today.month)[1] 
        dates = [today.replace(day=date) for date in range(1, end_day+1)]

    working_time = 0
    for date in dates:
        if  date.date() in red_days(date.year) or date.isoweekday() == DayEnum.SUN.value:
            working_time += RED_DAY_WORKING_TIME
        elif date.isoweekday() == DayEnum.SAT.value:
            working_time += SATURDAY_WORKING_TIME
        else:
            working_time += WEEKDAY_WORKING_TIME

    return working_time


PROGRESS_DETECTION = 'wheel_loader_000' # 이걸로 가정
START_X            = 200                # 작업구역 시작 x좌표
TURNING_X          = 1080               # 작업구역 끝 x좌표
PROGRESS_PER_ONE   = 20/20              # y축 방향 편도 1회당 공정률(%) = x축 방향 왕복 1회 공정률(%) / y축 방향 총 편도 반복횟수
                    ## 여기서 x축 방향 왕복 1회 공정률이 20 미만으로 떨어지면, progress가 정수로 모델링 되어 있어서 코드 수정 필요함
START_Y            = 120                # 작업구역 시작 y좌표
TURNING_Y          = 620                # 작업구역 끝 y좌표
INITIAL_PROGRESS   = 0                  # 작업 중간부터 detect 시작했을 경우 초기 공정률값 설정 가능
ERROR_RANGE        = 30