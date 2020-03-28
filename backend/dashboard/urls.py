from django.urls import path

from .views import (
    Dashboard,
    InputDashboard
)

from . import views

urlpatterns = [
    path('', Dashboard, name='dashboard'),
    path('input', InputDashboard, name='inputdashboard'),
]