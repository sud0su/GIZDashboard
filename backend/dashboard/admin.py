from django.contrib import admin

# Register your models here.
from .models import Undss

@admin.register(Undss)
class UndssAdmin(admin.ModelAdmin):
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