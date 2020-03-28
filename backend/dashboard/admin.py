from django.contrib import admin

# Register your models here.
from .models import Undss

@admin.register(Undss)
class UndssAdmin(admin.ModelAdmin):
    list_display = [
        'Data_Entry_No',
        'Province',
        'District',
        'Initiator',
        'Target',
        'Date'
        ]

# admin.site.register(Undss)