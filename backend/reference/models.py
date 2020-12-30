from django.db import models
from django.db.models import Min
from django.utils.translation import gettext as _

from dashboard.enumerations import MASTER_NAME

# Create your models here.
class Province(models.Model):
    name = models.CharField(_("Province"), max_length=50)

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(_("District"), max_length=50)
    province = models.ForeignKey(Province, verbose_name=_("Province"), on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class CityVillage(models.Model):
    name = models.CharField(_("City Village"), max_length=50)
    district = models.ForeignKey(District, verbose_name=_("District"), on_delete=models.CASCADE)
    province = models.ForeignKey(Province, verbose_name=_("Province"), on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Area(models.Model):
    name = models.CharField(_("Area Name"), max_length=50)
    district = models.ForeignKey(District, verbose_name=_("District"), on_delete=models.CASCADE)
    province = models.ForeignKey(Province, verbose_name=_("Province"), on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class IncidentType(models.Model):
    name = models.CharField(_("Incidient Type"), max_length=50)
    
    def __str__(self):
        return self.name

class IncidentSubtype(models.Model):
    name = models.CharField(_("Incident Sub Type"), max_length=50)
    incidenttype = models.ForeignKey(IncidentType, verbose_name=_("Incident Type"), on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class IncidentSourceManager(models.Manager):

    def min_id(self):
        return self.annotate(min_id=Min('id')).values_list('min_id', flat=True).first()

    def before_min_id(self):
        min_id = self.min_id()
        min_id = min_id if min_id == 0 else (min_id or 1)
        return min_id - 1

    def get_name(self, source_id):
        if source_id == str(self.before_min_id()):
            return MASTER_NAME
        return self.filter(id=source_id).values_list('name', flat=True).first()

    def get_prmo_id(self, prmo_name='PRMO'):
        return self.filter(name__iexact=prmo_name).values_list('id', flat=True).first()    

class IncidentSource(models.Model):
    objects = IncidentSourceManager()
    name = models.CharField(_("Incident Source"), max_length=50)

    def __str__(self):
        return self.name

class PrmoOffice(models.Model):
    name = models.CharField(_("PRMO Office Location"), max_length=50)
    
    def __str__(self):
        return self.name
