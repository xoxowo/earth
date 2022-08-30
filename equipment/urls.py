from django.urls import path

from equipment.views import EquipmonetListView, EquipmentDetailView

urlpatterns = [
   path('/list', EquipmonetListView.as_view()),
   path('/<int:equipment_id>', EquipmentDetailView.as_view()),
]