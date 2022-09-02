from django.urls import path

from .views import AreaListView, AreaDetailView

urlpatterns = [
    path('/list', AreaListView.as_view()),
    path('/detail/<str:area_name>', AreaDetailView.as_view()),    
]
