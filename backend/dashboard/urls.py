from django.urls import path

from .views import (
    Dashboard,
)

from . import views

urlpatterns = [
    path('', Dashboard, name='dashboard'),
]