from import_export import resources
from .models import Organization

class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        exclude = ('id',)
        fields = ('code', 'name',)
        import_id_fields = ('code',)
