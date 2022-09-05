from django.urls import path

from .views import AreaListView, AreaDetailView

urlpatterns = [
    path('/list', AreaListView.as_view()),
    path('/detail/<int:area_id>', AreaDetailView.as_view()),    
]
