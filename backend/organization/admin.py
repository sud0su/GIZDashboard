from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Organization
from .resources import OrganizationResource

@admin.register(Organization)
class OrganizationAdmin(ImportExportModelAdmin):
    list_display = [
        'code',
        'name',
        ]
    model = Organization
    resource_class = OrganizationResource
