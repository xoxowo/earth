from django.urls import path

from equipment.views import EquipmonetListView, EquipmentDetailView, AnalysisView

urlpatterns = [
   path('/list', EquipmonetListView.as_view()),
   path('/detail/<int:equipment_id>', EquipmentDetailView.as_view()),
   path('/analysis', AnalysisView.as_view()),
]