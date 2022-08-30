from django.urls import path

from detection.views import RealTimeView

urlpatterns = [
    path('', RealTimeView.as_view())
]