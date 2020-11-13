from reference.models import Province, District
from .resources import ProvinceResource, DistrictResource, CityVillageResource
from import_export.formats import base_formats
from django.urls import reverse_lazy
from giz.import_export_views import ImportView

class ProvinceImportView(ImportView):
    model = Province
    template_name = 'dashboard/import/reference_import_province.html'
    formats = (base_formats.XLSX,)
    resource_class = ProvinceResource
    success_url = reverse_lazy('importdataprovince')

    def create_dataset(self, *args, **kwargs):
        """ Insert an extra 'source_user' field into the data.
        """
        dataset = super().create_dataset(*args, **kwargs)
        length = len(dataset._data)
        dataset.append_col([self.request.user.id] * length,
                           header="source_user")
        return dataset

class DistrictImportView(ImportView):
    model = District
    template_name = 'dashboard/import/reference_import_district.html'
    formats = (base_formats.XLSX,)
    resource_class = DistrictResource
    success_url = reverse_lazy('importdatadistrict')

    def create_dataset(self, *args, **kwargs):
        """ Insert an extra 'source_user' field into the data.
        """
        dataset = super().create_dataset(*args, **kwargs)
        length = len(dataset._data)
        dataset.append_col([self.request.user.id] * length,
                           header="source_user")
        return dataset

# class DistrictImportView(ImportView):
#     model = District
#     template_name = 'dashboard/import/reference_import_province.html'
#     formats = (base_formats.XLSX,)
#     resource_class = DistrictResource
#     success_url = reverse_lazy('importdatadistrict')

#     def create_dataset(self, *args, **kwargs):
#         """ Insert an extra 'source_user' field into the data.
#         """
#         dataset = super().create_dataset(*args, **kwargs)
#         length = len(dataset._data)
#         dataset.append_col([self.request.user.id] * length,
#                            header="source_user")
#         return dataset

# class DistrictImportView(ImportView):
#     model = District
#     template_name = 'dashboard/import/reference_import_province.html'
#     formats = (base_formats.XLSX,)
#     resource_class = DistrictResource
#     success_url = reverse_lazy('importdatadistrict')

#     def create_dataset(self, *args, **kwargs):
#         """ Insert an extra 'source_user' field into the data.
#         """
#         dataset = super().create_dataset(*args, **kwargs)
#         length = len(dataset._data)
#         dataset.append_col([self.request.user.id] * length,
#                            header="source_user")
#         return dataset
