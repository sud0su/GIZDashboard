from django.db import models
from django.utils.translation import gettext as _


# Create your models here.
class Province(models.Model):
    name = models.CharField(_("Province"), max_length=50)

class District(models.Model):
    name = models.CharField(_("District"), max_length=50)
    provice = models.ForeignKey(Province, verbose_name=_("Province_"), on_delete=models.CASCADE)

class CityVillage(models.Model):
    name = models.CharField(_("City Village"), max_length=50)
    district = models.ForeignKey(District, verbose_name=_("District_"), on_delete=models.CASCADE)
    province = models.ForeignKey(Province, verbose_name=_("Province__"), on_delete=models.CASCADE)

class Area(models.Model):
    name = models.CharField(_("Area Name"), max_length=50)
    district = models.ForeignKey(District, verbose_name=_("District_"), on_delete=models.CASCADE)
    province = models.ForeignKey(Province, verbose_name=_("Province__"), on_delete=models.CASCADE)

class IncidentType(models.Model):
    name = models.CharField(_("Incidient Type"), max_length=50)

class IncidentSubtype(models.Model):
    name = models.CharField(_("Incident Sub Type"), max_length=50)
    incidenttype = models.ForeignKey(IncidentType, verbose_name=_("Incident Type"), on_delete=models.CASCADE)