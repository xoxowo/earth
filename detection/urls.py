from django.urls import path

from detection.views import RealTimeView, ProgressView

urlpatterns = [
    path('', RealTimeView.as_view()),
    path('progress', ProgressView.as_view()),
]