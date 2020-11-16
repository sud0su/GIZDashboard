from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from .models import Undss

@admin.register(Undss)
class UndssAdmin(ImportExportModelAdmin):
    list_display = [
        'Single_ID',
        'Province',
        'District',
        'Initiator',
        'Target',
        'Date',
        'created_at'
        ]

# admin.site.register(Undss)