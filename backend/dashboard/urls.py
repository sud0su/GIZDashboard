from django.urls import path, re_path

from .views import (
    Dashboard,
    DashboardPrint,
    InputDashboard,
    get_district,
    get_area_city,
    get_incident_subtype,
)

from . import views

urlpatterns = [
    path('input', InputDashboard, name='inputdashboard'),
    path('', Dashboard, name='dashboard'),
    re_path(r'^print$', DashboardPrint, name='dashboard_print'),
    # chained_dropdown_url
    path('get_district/<int:province_id>/', get_district, name='get_district'),
    path('get_area_city/<int:province_id>/<int:district_id>/', get_area_city, name='get_area_city'),
    path('get_incident_subtype/<int:incidenttype_id>/', get_incident_subtype, name='get_incident_subtype'),
]