from django.urls import path, re_path

from .views import (
    Dashboard,
    DashboardPrint,
    InputDashboard,
)

from . import views

urlpatterns = [
    path('', Dashboard, name='dashboard'),
    path('input', InputDashboard, name='inputdashboard'),
    re_path(r'^print$', DashboardPrint, name='dashboard_print'),
]