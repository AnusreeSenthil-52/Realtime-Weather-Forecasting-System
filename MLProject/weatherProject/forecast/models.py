from django.db import models


class WeatherData(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    data_type = models.CharField(max_length=50)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('latitude', 'longitude', 'data_type')
