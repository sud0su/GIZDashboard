from django.urls import path, re_path

from .views import (
    Dashboard,
    DashboardPrint,
    InputDashboard,
)

from . import views

urlpatterns = [
    path('input', InputDashboard, name='inputdashboard'),
    path('', Dashboard, name='dashboard'),
    re_path(r'^print$', DashboardPrint, name='dashboard_print'),
]