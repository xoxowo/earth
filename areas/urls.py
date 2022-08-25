
from django.urls import path
# from detection.views import startdetect
from .views import AreaDetailView

urlpatterns = [    
    path('/detail', AreaDetailView.as_view()),
]