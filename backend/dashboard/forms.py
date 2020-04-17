from django import forms
from .models import Undss
from django_select2.forms import Select2Widget
from bootstrap_datepicker_plus import DateTimePickerInput, TimePickerInput
from reference.models import Province, District, Area, CityVillage, IncidentType, IncidentSubtype
from organization.models import Organization

class UndssForm(forms.ModelForm):
    # Province = forms.ModelChoiceField(
    #     required=False,
    #     queryset=Province.objects.all(),
    #     widget= forms.Select(
    #         attrs={'data-placeholder':'Select Province', 'class':'select_province'}
    #     )
    #     # widget=Select2Widget(
    #     #     attrs={'data-placeholder':'Select Province', 'class':'select_province'}
    #     # )
    # )
    # District = forms.ModelChoiceField(
    #     required=False,
    #     queryset=District.objects.none(),
    #     widget= forms.Select(
    #         attrs={'data-placeholder':'Select District', 'class':'select_district'}
    #     )
    #     # widget=Select2Widget(
    #     #     attrs={'data-placeholder':'Select District'},
    #     # )
    # )
    # Area = forms.ModelChoiceField(
    #     required=False,
    #     queryset=Area.objects.none(),
    #     widget=Select2Widget(
    #         attrs={'data-placeholder':'Select Area'}
    #     )
    # )
    # City_Village = forms.ModelChoiceField(
    #     required=False,
    #     queryset=CityVillage.objects.none(),
    #     widget=Select2Widget(
    #         attrs={'data-placeholder':'Select City Village'}
    #     )
    # )
    # Incident_Type = forms.ModelChoiceField(
    #     required=False,
    #     queryset=IncidentType.objects.all(),
    #     widget=Select2Widget(
    #         attrs={'data-placeholder':'Select Incident Type'}
    #     )
    # )
    # Incident_Subtype = forms.ModelChoiceField(
    #     required=False,
    #     queryset=IncidentSubtype.objects.none(),
    #     widget=Select2Widget(
    #         attrs={'data-placeholder':'Select Incident Subtype'}
    #     )
    # )
    # Initiator = forms.ModelChoiceField(
    #     required=False,
    #     queryset=Organization.objects.all(),
    #     widget=Select2Widget(
    #         attrs={'data-placeholder':'Select Initiator'}
    #     )
    # )
    # Target = forms.ModelChoiceField(
    #     required=False,
    #     queryset=Organization.objects.all(),
    #     widget=Select2Widget(
    #         attrs={'data-placeholder':'Select Target'}
    #     )
    # )

    class Meta:
        model = Undss
        fields = [
            'Shape',
            'Data_Entry_No',
            'Date',
            'Time_of_Incident',
            'Province',
            'District',
            'City_Village',
            'Area',
            'Police_District',
            'Incident_Type',
            'Incident_Subtype',
            'Description_of_Incident',
            'HPA',
            'Initiator',
            'Target',
            'killed',
            'Injured',
            'Abducted',
            'Latitude',
            'Longitude',
            'PRMO',
            'UNDSS',
            'INSO',
        ]
        widgets = {
            'Date': DateTimePickerInput(), 
            'Time_of_Incident': TimePickerInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['District'].queryset = District.objects.none()
        self.fields['Incident_Subtype'].queryset = IncidentSubtype.objects.none()

        if 'Province' in self.data:
            try:
                province_id = int(self.data.get('Province'))
                self.fields['District'].queryset = District.objects.filter(province_id=province_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['District'].queryset = self.instance.Province.objects.all().order_by('name')

        if 'Incident_Type' in self.data:
            try:
                incidenttype_id = int(self.data.get('Incident_Type'))
                self.fields['Incident_Subtype'].queryset = IncidentSubtype.objects.filter(incidenttype__id=incidenttype_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['Incident_Type'].queryset = self.instance.Incident_Type.objects.all().order_by('name')