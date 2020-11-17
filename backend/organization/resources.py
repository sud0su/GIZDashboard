from import_export import resources
from .models import Organization

class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        exclude = ('id',)
        import_id_fields = ('code', 'name',)
