from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
# Register your models here.
from .models import Province, District, IncidentType, IncidentSubtype, IncidentSource
from .resources import DistrictResource, ProvinceResource, IncidentTypeResource, IncidentSubTypeResource, IncidentSourceResource

@admin.register(Province)
class ProvinceAdmin(ImportExportModelAdmin):
    
    model = Province
    resource_class = ProvinceResource

@admin.register(District)
class DistrictAdmin(ImportExportModelAdmin):
    list_display = [
        'name',
        'province',
        ]
    list_filter = ('province',)
    model = District
    resource_class = DistrictResource

@admin.register(IncidentType)
class IncidentTypeAdmin(ImportExportModelAdmin):
    model = IncidentType
    resource_class = IncidentTypeResource

@admin.register(IncidentSubtype)
class IncidentSubtypeAdmin(ImportExportModelAdmin):
    list_display = [
        'name',
        'incidenttype',
        ]
    list_filter = ('incidenttype',)
    model = IncidentSubtype
    resource_class = IncidentSubTypeResource

@admin.register(IncidentSource)
class IncidentSourceAdmin(ImportExportModelAdmin):
    model = IncidentSource
    resource_class = IncidentSourceResource
