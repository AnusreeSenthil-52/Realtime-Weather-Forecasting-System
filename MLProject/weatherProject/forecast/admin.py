from django.contrib import admin
from .models import WeatherData


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longitude', 'data_type', 'timestamp')
    search_fields = ('latitude', 'longitude', 'data_type')
