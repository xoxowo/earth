from django.db import models

from area.models      import Area

class Equipment(models.Model):
    id            = models.AutoField(primary_key=True)
    company       = models.CharField(max_length=45)
    serial_number = models.CharField(max_length=45)
    type          = models.ForeignKey('detection.DetectionType', on_delete=models.CASCADE, related_name='equipment')
    area          = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='equipment')

    class Meta: 
        db_table = 'equipment'