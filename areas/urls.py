
from django.urls import path

from .views import AreaListView

urlpatterns = [
    path('/list', AreaListView.as_view()),
]