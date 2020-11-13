from django.db.models import fields
from import_export import resources
from .models import Province, District, CityVillage, Area, IncidentType, IncidentSubtype, IncidentSource


class ProvinceResource(resources.ModelResource):
    class Meta:
        model = Province
        exclude = ('id',)
        import_id_fields = ('name',)

    # def before_import(self, dataset, using_transactions=True, dry_run=False, **kwargs):
    #     # num_rows = dataset.height
    #     # print('num_rows in dataset: {}'.format(num_rows))
    #     print(dataset)
    # def before_import_row(self, row, **kwargs):
    #     province = row.get('province')
    #     (cat, _created) = Province.objects.get_or_create(name=province)
    #     row['category'] = cat.id


class DistrictResource(resources.ModelResource):
    class Meta:
        model = District
        exclude = ('id',)
        # fields = ('name', 'province__name', )
        import_id_fields = ('name',)

    def before_import_row(self, row, **kwargs):
        province = row.get('province')
        (prov, _created) = Province.objects.get_or_create(name=province)
        row['province'] = prov.id


class CityVillageResource(resources.ModelResource):
    class Meta:
        model = CityVillage
        exclude = ('id',)
        import_id_fields = ('name',)
