from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from .models import Undss
from .resources import UndssResource

@admin.register(Undss)
class UndssAdmin(ImportExportModelAdmin):
    list_display = [
        'Single_ID',
        'Province',
        'District',
        'Initiator',
        'Target',
        'Date',
        'Incident_Source',
        'created_at'
        ]
    model = Undss
    ordering = ('-created_at',)
    list_filter = ('created_at', 'Province', 'Target')
    resource_class = UndssResource

# admin.site.register(Undss)