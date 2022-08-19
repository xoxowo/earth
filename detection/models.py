
from django.db import models

class Camera(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'cameras'

class DetectionType(models.Model):
    id   = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'detection_types'

class State(models.Model):
    id    = models.AutoField(primary_key=True)
    state = models.CharField(max_length=45)

    class Meta:
        db_table = 'states'

class Detection(models.Model):
    id             = models.AutoField(primary_key=True)
    x              = models.IntegerField()
    y              = models.IntegerField()
    width          = models.IntegerField()
    height         = models.IntegerField()
    datetime       = models.DateTimeField()
    cam            = models.ForeignKey(Camera, on_delete=models.CASCADE)
    detection_type = models.ForeignKey(DetectionType, on_delete=models.CASCADE)
    state          = models.ForeignKey(State, on_delete=models.CASCADE)

    class Meta:
        db_table = 'detections'

