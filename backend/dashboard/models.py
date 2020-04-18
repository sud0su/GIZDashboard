import os
import time
from uuid import uuid4
from django.utils.deconstruct import deconstructible
from django.db import models
from datetime import datetime, timedelta
from django.contrib import admin
from django.utils.translation import gettext as _
from reference.models import Province, District, CityVillage, Area, IncidentType, IncidentSubtype
from organization.models import Organization
from django.urls import reverse

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        fullpath = self.path+'{}'.format(time.strftime("%Y/%m/%d"))
        return os.path.join(fullpath , filename)

def default_start_time():
    now = datetime.now()
    start = now.replace(hour=22, minute=0, second=0, microsecond=0)
    return start if start > now else start + timedelta(days=1)  

# Create your models here.
mediaPath = PathAndRename("shape/")
class Undss(models.Model):
    Shape = models.FileField(_("Shape"), upload_to=mediaPath, null=True, blank=True)
    Data_Entry_No = models.CharField(_("Data Entry No"), max_length=50, null=True, blank=True)
    Date = models.DateTimeField(_("Date"), auto_now=False, auto_now_add=False, null=True, blank=True)
    Time_of_Incident = models.TimeField(_("Time Of Incident"), default=default_start_time, null=True, blank=True)
    Province = models.ForeignKey(Province, verbose_name=_("Province"), on_delete=models.CASCADE, null=True, blank=True)
    District =models.ForeignKey(District, verbose_name=_("District"), on_delete=models.CASCADE, null=True, blank=True)
    City_Village = models.ForeignKey(CityVillage, verbose_name=_("City Village"), on_delete=models.CASCADE, null=True, blank=True)
    Area = models.ForeignKey(Area, verbose_name=_("Area"), on_delete=models.CASCADE, null=True, blank=True)
    Police_District = models.CharField(max_length=255, null=True, blank=True)
    Incident_Type = models.ForeignKey(IncidentType, verbose_name=_("Incident Type"), on_delete=models.CASCADE, null=True, blank=True)
    Incident_Subtype = models.ForeignKey(IncidentSubtype, verbose_name=_("Incident SubType"), on_delete=models.CASCADE, null=True, blank=True)
    Description_of_Incident = models.CharField(max_length=255, null=True, blank=True)
    HPA = models.CharField(max_length=255, null=True, blank=True)
    Initiator = models.ForeignKey(Organization, related_name="Organization_initiator_name", on_delete=models.CASCADE, null=True, blank=True)
    Target = models.ForeignKey(Organization, related_name="Organization_target_name", on_delete=models.CASCADE, null=True, blank=True)
    killed = models.PositiveIntegerField(null=True, blank=True)
    Field16 = models.PositiveIntegerField(null=True, blank=True)
    Field17 = models.PositiveIntegerField(null=True, blank=True)
    Field18 = models.PositiveIntegerField(null=True, blank=True)
    Field19 = models.PositiveIntegerField(null=True, blank=True)
    Field20 = models.PositiveIntegerField(null=True, blank=True)
    Field21 = models.PositiveIntegerField(null=True, blank=True)
    Injured = models.PositiveIntegerField(null=True, blank=True)
    Field23 = models.PositiveIntegerField(null=True, blank=True)
    Field24 = models.PositiveIntegerField(null=True, blank=True)
    Field25 = models.PositiveIntegerField(null=True, blank=True)
    Field26 = models.PositiveIntegerField(null=True, blank=True)
    Field27 = models.PositiveIntegerField(null=True, blank=True)
    Field28 = models.PositiveIntegerField(null=True, blank=True)
    Abducted = models.PositiveIntegerField(null=True, blank=True)
    Field30 = models.PositiveIntegerField(null=True, blank=True)
    Field31 = models.PositiveIntegerField(null=True, blank=True)
    Field32 = models.PositiveIntegerField(null=True, blank=True)
    Field33 = models.PositiveIntegerField(null=True, blank=True)
    Latitude = models.FloatField(null=True, blank=True)
    Longitude = models.FloatField(null=True, blank=True)
    PRMO = models.CharField(max_length=255, null=True, blank=True)
    UNDSS = models.CharField(max_length=255, null=True, blank=True)
    INSO = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.Data_Entry_No
    
    def get_absolute_url(self):
        return reverse("detail", kwargs={"pk": self.pk})
    
    class Meta:
        ordering = ('-created_at',)
