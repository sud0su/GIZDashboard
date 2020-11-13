from import_export import resources
from .models import Undss


class UndssResource(resources.ModelResource):
    class Meta:
        model = Undss
        exclude = ('id', 'created_at' , 'updated_at',)

    # def before_import(self, dataset, using_transactions=True, dry_run=False, **kwargs):
    #     # num_rows = dataset.height
    #     # print('num_rows in dataset: {}'.format(num_rows))
    #     print(dataset)
    # def before_import_row(self, row, **kwargs):
    #     province = row.get('province')
    #     (cat, _created) = Province.objects.get_or_create(name=province)
    #     row['category'] = cat.id
