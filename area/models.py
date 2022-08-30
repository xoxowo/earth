from django.db import models

class Area(models.Model):
    id            = models.AutoField(primary_key=True)
    name          = models.CharField(max_length=45)
    address       = models.CharField(max_length=200)
    latitude      = models.DecimalField(max_digits=12, decimal_places=6)
    longitude     = models.DecimalField(max_digits=12, decimal_places=6)
    cam_latitude  = models.DecimalField(max_digits=12, decimal_places=6)
    cam_longitude = models.DecimalField(max_digits=12, decimal_places=6)

    class Meta:
        db_table = 'area'