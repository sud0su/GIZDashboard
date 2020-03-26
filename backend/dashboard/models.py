from django.db import models
from datetime import datetime    
from django.contrib import admin
from django.utils.translation import gettext as _
from reference.models import Province, District, CityVillage, Area, IncidentType, IncidentSubtype

# Create your models here.
class Undss(models.Model):
    Shape = models.BinaryField()
    Data_Entry_No = models.CharField(_("Data Entry No"), max_length=50)
    Date = models.DateTimeField(default=datetime.now, blank=True)
    Time_of_Incident = models.CharField(max_length=255)
    Province = models.ForeignKey(Province, verbose_name=_("Province"), on_delete=models.CASCADE)
    District =models.ForeignKey(District, verbose_name=_("District"), on_delete=models.CASCADE)
    City_Village = models.ForeignKey(CityVillage, verbose_name=_("City Village"), on_delete=models.CASCADE)
    Area = models.ForeignKey(Area, verbose_name=_("Area"), on_delete=models.CASCADE)
    Police_District = models.CharField(max_length=255)
    Incident_Type = models.ForeignKey(IncidentType, verbose_name=_("Incident Type"), on_delete=models.CASCADE)
    Incident_Subtype = models.ForeignKey(IncidentSubtype, verbose_name=_("Incidenet SubType"), on_delete=models.CASCADE)
    Description_of_Incident = models.CharField(max_length=255)
    HPA = models.CharField(max_length=255)
    Initiator = models.CharField(max_length=255)
    Target = models.CharField(max_length=255)
    killed = models.PositiveIntegerField()
    Field16 = models.PositiveIntegerField()
    Field17 = models.PositiveIntegerField()
    Field18 = models.PositiveIntegerField()
    Field19 = models.PositiveIntegerField()
    Field20 = models.PositiveIntegerField()
    Field21 = models.PositiveIntegerField()
    Injured = models.PositiveIntegerField()
    Field23 = models.PositiveIntegerField()
    Field24 = models.PositiveIntegerField()
    Field25 = models.PositiveIntegerField()
    Field26 = models.PositiveIntegerField()
    Field27 = models.PositiveIntegerField()
    Field28 = models.PositiveIntegerField()
    Abducted = models.PositiveIntegerField()
    Field30 = models.PositiveIntegerField()
    Field31 = models.PositiveIntegerField()
    Field32 = models.PositiveIntegerField()
    Field33 = models.PositiveIntegerField()
    Latitude = models.FloatField()
    Longitude = models.FloatField()
    PRMO = models.CharField(max_length=255)
    UNDSS = models.CharField(max_length=255)
    INSO = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
