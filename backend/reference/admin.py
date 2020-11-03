from django.contrib import admin

# Register your models here.
from .models import Province, District, CityVillage, Area, IncidentType, IncidentSubtype, IncidentSource

admin.site.register(Province)
admin.site.register(District)
admin.site.register(CityVillage)
admin.site.register(Area)
admin.site.register(IncidentType)
admin.site.register(IncidentSubtype)
admin.site.register(IncidentSource)
