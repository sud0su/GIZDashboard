from django import forms
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from reference.models import Province, District, IncidentType, IncidentSubtype

# Register your models here.
from .models import Undss
from .resources import UndssResource

class UndssAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        province_id = self.data.get('Province') or self.instance.Province_id
        if province_id:
            self.fields['District'].queryset = District.objects.filter(province_id=province_id).order_by('name')

        incidenttype_id = self.data.get('Incident_Type') or self.instance.Incident_Type_id
        if incidenttype_id:
            self.fields['Incident_Subtype'].queryset = IncidentSubtype.objects.filter(incidenttype_id=incidenttype_id).order_by('name')

    class Media:
        js = ('js/admin-undss.js',)

@admin.register(Undss)
class UndssAdmin(ImportExportModelAdmin):
    list_display = [
        'Single_ID',
        'Province',
        'District',
        'Initiator',
        'Target',
        'Date',
        'Incident_Source',
        'created_at'
        ]
    model = Undss
    form = UndssAdminForm
    ordering = ('-created_at',)
    list_filter = ('created_at', 'Incident_Source', 'Province', 'Target', )
    resource_class = UndssResource

# admin.site.register(Undss)