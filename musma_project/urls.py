from django.urls import path, include

urlpatterns = [
    path('', include('detection.urls')),
    path('equipment', include('equipment.urls')),
    path('area', include('area.urls')),
]