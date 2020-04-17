from django.urls import path, re_path

from .views import (
    Dashboard,
    DashboardPrint,
    # InputUndss,
    InputUndssView,
    UndssDetailView,
    get_district,
    get_area_city,
    get_incident_subtype,
    load_district,
    load_subtype,
    load_area,
    load_cityillage
)

from . import views

urlpatterns = [
    path('', Dashboard, name='dashboard'),
    # path('input/', InputUndss, name='inputdashboard'),
    re_path(r'^print$', DashboardPrint, name='dashboard_print'),
    path('input/', InputUndssView.as_view(), name='inputdashboard'),
    path('undssdetail/<int:pk>/', UndssDetailView.as_view(), name='detail'),
    # chained_dropdown_url
    path('get_district/<int:province_id>/', get_district, name='get_district'),
    path('get_area_city/<int:province_id>/<int:district_id>/', get_area_city, name='get_area_city'),
    path('get_incident_subtype/<int:incidenttype_id>/', get_incident_subtype, name='get_incident_subtype'),

    path('get/district/', load_district, name='ajax_load_district'), 
    path('get/subtype/', load_subtype, name='ajax_load_subtype'), 
    path('get/area/', load_area, name='ajax_load_area'), 
    path('get/cityvlillage/', load_cityillage, name='ajax_load_cityillage'), 

]