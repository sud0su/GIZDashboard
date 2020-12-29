from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Province, District, IncidentType, IncidentSubtype, IncidentSource, PrmoOffice
from django.core.exceptions import ValidationError

class ProvinceResource(resources.ModelResource):
    class Meta:
        model = Province
        exclude = ('id',)
        import_id_fields = ('name',)


class IncidentSourceResource(resources.ModelResource):
    class Meta:
        model = IncidentSource
        exclude = ('id',)
        import_id_fields = ('name',)


class PrmoOfficeResource(resources.ModelResource):
    class Meta:
        model = PrmoOffice
        exclude = ('id',)
        import_id_fields = ('name',)


class IncidentTypeResource(resources.ModelResource):
    class Meta:
        model = IncidentType
        exclude = ('id',)
        import_id_fields = ('name',)

# class IncidentTypeForeignKey(ForeignKeyWidget):
#     def get_queryset(self, value, row, *args, **kwargs):
#         return self.model.objects.filter(name=value)

class IncidentSubTypeResource(resources.ModelResource):
    name = fields.Field(column_name='IncidentSubType', attribute='name')
    incidenttype = fields.Field(column_name='IncidentType', attribute='incidenttype', widget=ForeignKeyWidget(IncidentType, 'name'))

    class Meta:
        model = IncidentSubtype
        exclude = ('id',)
        fields = ('name', 'incidenttype',)
        clean_model_instances = True
        import_id_fields = ('name', 'incidenttype')

    def before_import_row(self, row, **kwargs):
        inctype = row.get('IncidentType')
        istype = IncidentType.objects.filter(name=inctype)
        if not bool(istype):
            raise ValidationError('Incident Type name %s cannot be found' % inctype)



class DistrictResource(resources.ModelResource):
    name = fields.Field(column_name='District', attribute='name')
    province = fields.Field(column_name='Province', attribute='province', widget=ForeignKeyWidget(Province, 'name'))

    class Meta:
        model = District
        exclude = ('id',)
        fields = ('name', 'province',)
        clean_model_instances = True
        import_id_fields = ('name', 'province')

    def before_import_row(self, row, **kwargs):
        province = row.get('Province')
        prov = Province.objects.filter(name=province)
        if not bool(prov):
            raise ValidationError('Province name %s cannot be found' % province)
