from django.urls import path
from .views import ProvinceImportView, DistrictImportView
from django.views.generic import TemplateView

urlpatterns = [
    path('import/', TemplateView.as_view(template_name="dashboard/import/reference_import.html"), name='importdata'),
    path('import/import_province/', ProvinceImportView.as_view(), name='importdataprovince'),
    path('import/confirm_import_province/', ProvinceImportView.as_view(confirm=True), name='confirmimportdataprovince'),
    path('import/import_district/', DistrictImportView.as_view(), name='importdatadistrict'),
    path('import/confirm_import_district/', DistrictImportView.as_view(confirm=True), name='confirmimportdatadistrict'),
]
