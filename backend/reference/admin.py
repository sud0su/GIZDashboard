from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
# Register your models here.
from .models import Province, District, CityVillage, Area, IncidentType, IncidentSubtype, IncidentSource

@admin.register(Province, District, CityVillage, Area, IncidentType, IncidentSubtype, IncidentSource)

class ViewAdmin(ImportExportModelAdmin):
    pass

# @admin.register(Province)
# class ProvinceAdmin(ImportExportModelAdmin):
#     pass

# @admin.register(District)
# class DistrictAdmin(ImportExportModelAdmin):
#     pass

# @admin.register(CityVillage)
# class CityVillageAdmin(ImportExportModelAdmin):
#     pass

# @admin.register(Area)
# class AreaAdmin(ImportExportModelAdmin):
#     pass

# @admin.register(IncidentType)
# class IncidentTypeAdmin(ImportExportModelAdmin):
#     pass

# @admin.register(IncidentSubtype)
# class IncidentSubtypeAdmin(ImportExportModelAdmin):
#     pass

# @admin.register(IncidentSource)
# class IncidentSourceAdmin(ImportExportModelAdmin):
#     pass
