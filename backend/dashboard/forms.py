from django import forms
from .models import Undss
from django_select2.forms import Select2Widget, ModelSelect2Widget
from bootstrap_datepicker_plus import DateTimePickerInput, TimePickerInput
from reference.models import Province, District, Area, CityVillage, IncidentType, IncidentSubtype
from organization.models import Organization

class UndssForm(forms.ModelForm):
    Province = forms.ModelChoiceField(
        required=False,
        queryset=Province.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder':'Select Province'}
        )
    )

    # District = forms.ModelChoiceField(
    #     required=False,
    #     queryset=District.objects.none(),
    #     widget=Select2Widget(
    #         attrs={'data-placeholder':'Select District'}
    #     )
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
 
    # def clean(self):
    #     for field, value in self.cleaned_data.items():

    #         print(field,'==',value)
    #         self.cleaned_data['field'] = value.lower()

