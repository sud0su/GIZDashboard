from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Organization
from .resources import OrganizationResource

@admin.register(Organization)
class OrganizationAdmin(ImportExportModelAdmin):
    model = Organization
    resource_class = OrganizationResource
