import os
import time
from uuid import uuid4
from django.utils.deconstruct import deconstructible
from django.db import models
from datetime import datetime, timedelta, time
from django.utils.translation import gettext as _
from reference.models import Province, District, IncidentType, IncidentSubtype, IncidentSource
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
    # Shape = models.FileField(_("Shape"), upload_to=mediaPath, null=True, blank=True)
    Single_ID = models.CharField(_("Data Entry No"), max_length=50, null=True, blank=False)
    Date = models.DateField(_("Date"), auto_now=False, auto_now_add=False, null=True, blank=False)
    Time_of_Incident = models.TimeField(_("Time Of Incident"), default=time(), null=False, blank=False)
    # Time_of_Incident = models.TimeField(_("Time Of Incident"), default=default_start_time, null=True, blank=True)
    Province = models.ForeignKey(Province, verbose_name=_("Province"), on_delete=models.CASCADE, null=True, blank=False)
    District =models.ForeignKey(District, verbose_name=_("District"), on_delete=models.CASCADE, null=True, blank=False)
    # City_Village = models.ForeignKey(CityVillage, verbose_name=_("City Village"), on_delete=models.CASCADE, null=True, blank=True)
    City_Village = models.CharField(verbose_name=_("City Village"), max_length=255, null=True, blank=True)
    # Area = models.ForeignKey(Area, verbose_name=_("Area"), on_delete=models.CASCADE, null=True, blank=True)
    Area = models.CharField(verbose_name=_("Area"), max_length=255, null=True, blank=True)
    Police_District = models.CharField(max_length=255, null=True, blank=True)
    Incident_Type = models.ForeignKey(IncidentType, verbose_name=_("Incident Type"), on_delete=models.CASCADE, null=True, blank=False)
    Incident_Subtype = models.ForeignKey(IncidentSubtype, verbose_name=_("Incident SubType"), on_delete=models.CASCADE, null=True, blank=True)
    Description_of_Incident = models.TextField(_("Description of Incident"), null=True, blank=True)
    # Description_of_Incident = models.CharField(max_length=255, null=True, blank=True)
    HPA = models.CharField(max_length=255, null=True, blank=True)
    Initiator = models.ForeignKey(Organization, related_name="Organization_initiator_name", on_delete=models.CASCADE, null=True, blank=False)
    Target = models.ForeignKey(Organization, related_name="Organization_target_name", on_delete=models.CASCADE, null=True, blank=False)
    Kill_Natl = models.PositiveIntegerField(verbose_name='Killed - National', default=0, null=True, blank=True)
    Kill_Intl = models.PositiveIntegerField(verbose_name='Killed - International', default=0, null=True, blank=True)
    Kill_ANSF = models.PositiveIntegerField(verbose_name='Killed - ANSF', default=0, null=True, blank=True)
    Kill_IM = models.PositiveIntegerField(verbose_name='Killed - IM', default=0, null=True, blank=True)
    Kill_ALP_PGM = models.PositiveIntegerField(verbose_name='Killed - ALP_PGM', default=0, null=True, blank=True)
    Kill_AOG = models.PositiveIntegerField(verbose_name='Killed - AOG', default=0, null=True, blank=True)
    Kill_ISKP = models.PositiveIntegerField(verbose_name='Killed - ISKP', default=0, null=True, blank=True)
    Inj_Natl = models.PositiveIntegerField(verbose_name='Injured - National', default=0, null=True, blank=True)
    Inj_Intl = models.PositiveIntegerField(verbose_name='Injured - International', default=0, null=True, blank=True)
    Inj_ANSF = models.PositiveIntegerField(verbose_name='Injured - ANSF', default=0, null=True, blank=True)
    Inj_IM = models.PositiveIntegerField(verbose_name='Injured - IM', default=0, null=True, blank=True)
    Inj_ALP_PGM = models.PositiveIntegerField(verbose_name='Injured - ALP_PGM', default=0, null=True, blank=True)
    Inj_AOG = models.PositiveIntegerField(verbose_name='Injured - AOG', default=0, null=True, blank=True)
    Inj_ISKP = models.PositiveIntegerField(verbose_name='Injured - ISKP', default=0, null=True, blank=True)
    Abd_Natl = models.PositiveIntegerField(verbose_name='Abducted - National', default=0,null=True, blank=True)
    Abd_Intl = models.PositiveIntegerField(verbose_name='Abducted - International', default=0,null=True, blank=True)
    Abd_ANSF = models.PositiveIntegerField(verbose_name='Abducted - ANSF', default=0,null=True, blank=True)
    Abd_IM = models.PositiveIntegerField(verbose_name='Abducted - IM', default=0,null=True, blank=True)
    Abd_ALP_PGM = models.PositiveIntegerField(verbose_name='Abducted - ALP_PGM', default=0,null=True, blank=True)
    Latitude = models.FloatField(null=True, blank=True)
    Longitude = models.FloatField(null=True, blank=True)
    Incident_Source = models.ForeignKey(IncidentSource, on_delete=models.CASCADE, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.Single_ID
    
    def get_absolute_url(self):
        return reverse("detail", kwargs={"pk": self.pk})
    
    class Meta:
        # ordering = ('-created_at',)
        pass
