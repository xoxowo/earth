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
