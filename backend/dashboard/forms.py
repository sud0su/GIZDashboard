from django import forms
from .models import Undss, MasterIncident
from django_select2.forms import Select2Widget
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput
from reference.models import Province, District, Area, CityVillage, IncidentType, IncidentSubtype, IncidentSource, PrmoOffice
from organization.models import Organization


class UndssForm(forms.ModelForm):
    Date = forms.DateField(
        input_formats=['%m-%d-%Y'],
        widget=DatePickerInput(format='%m-%d-%Y')
    )
    Province = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Province',
                   'class': 'select_province'}
        )
    )
    District = forms.ModelChoiceField(
        queryset=District.objects.none(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select District'},
        )
    )
    Incident_Type = forms.ModelChoiceField(
        queryset=IncidentType.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Incident Type'}
        )
    )
    Incident_Subtype = forms.ModelChoiceField(
        required=False,
        queryset=IncidentSubtype.objects.none(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Incident Subtype'}
        )
    )
    Initiator = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Initiator'}
        )
    )
    Target = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Target'}
        )
    )
    # Incident_Source_Choice = (
    #     ('PRMO', 'PRMO'),
    #     ('INSO', 'INSO'),
    #     ('UNDSS', 'UNDSS'),
    # )
    Incident_Source = forms.ModelChoiceField(
        # queryset=IncidentSource.objects.none(),
        queryset=IncidentSource.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Incident Source'}
        )
    )
    Prmo_Office = forms.ModelChoiceField(
        required=False,
        queryset=PrmoOffice.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select PRMO Office Location'}
        )
    )
    HPA = forms.ChoiceField(
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select HPA'}
        )
    )
    IGCHO = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=((False, 'No'), (True, 'Yes')),
                                  widget=Select2Widget(
        attrs={'data-placeholder': 'Select HPA'}
    ))

    class Meta:
        model = Undss
        fields = [
            'Single_ID',
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
            'IGCHO',
            'Kill_Natl',
            'Kill_Intl',
            'Kill_ANSF',
            'Kill_IM',
            'Kill_ALP_PGM',
            'Kill_AOG',
            'Kill_ISKP',
            'Inj_Natl',
            'Inj_Intl',
            'Inj_ANSF',
            'Inj_IM',
            'Inj_ALP_PGM',
            'Inj_AOG',
            'Inj_ISKP',
            'Abd_Natl',
            'Abd_Intl',
            'Abd_ANSF',
            'Abd_IM',
            'Abd_ALP_PGM',
            'Latitude',
            'Longitude',
            'Incident_Source',
            'Incident_Source_Office',
            # 'PRMO',
            # 'UNDSS',
            # 'INSO',
        ]
        widgets = {
            # 'Date': DatePickerInput(format='%m-%d-%Y'),
            'Time_of_Incident': TimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['District'].queryset = District.objects.none()
        self.fields['Incident_Subtype'].queryset = IncidentSubtype.objects.none()
        # self.fields['Incident_Source'].queryset = IncidentSource.objects.all(
        # ).order_by('name')

        if 'Province' in self.data:
            try:
                province_id = int(self.data.get('Province'))
                self.fields['District'].queryset = District.objects.filter(
                    province_id=province_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['Province'].queryset = self.instance.Province.objects.all(
            ).order_by('name')

        if 'Incident_Type' in self.data:
            try:
                incidenttype_id = int(self.data.get('Incident_Type'))
                self.fields['Incident_Subtype'].queryset = IncidentSubtype.objects.filter(
                    incidenttype__id=incidenttype_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['Incident_Type'].queryset = self.instance.Incident_Type.objects.all(
            ).order_by('name')

        if 'District' in self.data:
            try:
                province_id = int(self.data.get('Province'))
                district_id = int(self.data.get('District'))
                self.fields['Area'].queryset = Area.objects.filter(
                    province__id=province_id, district_id=district_id).order_by('name')
                self.fields['City_Village'].queryset = CityVillage.objects.filter(
                    province__id=province_id, district_id=district_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['District'].queryset = self.instance.District.objects.all(
            ).order_by('name')
            self.fields['Province'].queryset = self.instance.Province.objects.all(
            ).order_by('name')


class MasterIncidentForm(forms.ModelForm):

    Date = forms.DateField(
        input_formats=['%m-%d-%Y'],
        widget=DatePickerInput(format='%m-%d-%Y')
    )
    Province = forms.ModelChoiceField(
        # required=False,
        queryset=Province.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Province',
                   'class': 'select_province'}
        )
    )
    District = forms.ModelChoiceField(
        # required=False,
        queryset=District.objects.none(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select District'},
        )
    )
    Incident_Type = forms.ModelChoiceField(
        # required=False,
        queryset=IncidentType.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Incident Type'}
        )
    )
    Incident_Subtype = forms.ModelChoiceField(
        required=False,
        queryset=IncidentSubtype.objects.none(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Incident Subtype'}
        )
    )
    Initiator = forms.ModelChoiceField(
        # required=False,
        queryset=Organization.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Initiator'}
        )
    )
    Target = forms.ModelChoiceField(
        # required=False,
        queryset=Organization.objects.all(),
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select Target'}
        )
    )
    # Incident_Source = forms.ModelChoiceField(
    #     # required=False,
    #     queryset=IncidentSource.objects.none(),
    #     widget=Select2Widget(
    #         attrs={'data-placeholder': 'Select Incident Source'}
    #     )
    # )
    HPA = forms.ChoiceField(
        # required=False,
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=Select2Widget(
            attrs={'data-placeholder': 'Select HPA'}
        )
    )

    IGCHO = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=((False, 'No'), (True, 'Yes')),
                                  widget=Select2Widget(
        attrs={'data-placeholder': 'Select HPA'}
    ))

    PRMO = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=((False, 'No'), (True, 'Yes')),
                                  widget=Select2Widget(
        attrs={'data-placeholder': 'Select PRMO'}
    ))

    UNDSS = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=((False, 'No'), (True, 'Yes')),
                                  widget=Select2Widget(
        attrs={'data-placeholder': 'Select UNDSS'}
    ))

    INSO = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=((False, 'No'), (True, 'Yes')),
                                  widget=Select2Widget(
        attrs={'data-placeholder': 'Select INSO'}
    ))

    class Meta:
        model = MasterIncident
        fields = [
            # 'Shape',
            'Single_ID',
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
            'IGCHO',
            'Kill_Natl',
            'Kill_Intl',
            'Kill_ANSF',
            'Kill_IM',
            'Kill_ALP_PGM',
            'Kill_AOG',
            'Kill_ISKP',
            'Inj_Natl',
            'Inj_Intl',
            'Inj_ANSF',
            'Inj_IM',
            'Inj_ALP_PGM',
            'Inj_AOG',
            'Inj_ISKP',
            'Abd_Natl',
            'Abd_Intl',
            'Abd_ANSF',
            'Abd_IM',
            'Abd_ALP_PGM',
            'Latitude',
            'Longitude',
            # 'Incident_Source',
            'PRMO',
            'UNDSS',
            'INSO',
        ]
        widgets = {
            # 'Date': DatePickerInput(format='%m-%d-%Y'),
            'Time_of_Incident': TimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['District'].queryset = District.objects.none()
        self.fields['Incident_Subtype'].queryset = IncidentSubtype.objects.none()
        # self.fields['Incident_Source'].queryset = IncidentSource.objects.all(
        # ).order_by('name')

        if 'Province' in self.data:
            try:
                province_id = int(self.data.get('Province'))
                self.fields['District'].queryset = District.objects.filter(
                    province_id=province_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['Province'].queryset = self.instance.Province.objects.all(
            ).order_by('name')

        if 'Incident_Type' in self.data:
            try:
                incidenttype_id = int(self.data.get('Incident_Type'))
                self.fields['Incident_Subtype'].queryset = IncidentSubtype.objects.filter(
                    incidenttype__id=incidenttype_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['Incident_Type'].queryset = self.instance.Incident_Type.objects.all(
            ).order_by('name')

        if 'District' in self.data:
            try:
                province_id = int(self.data.get('Province'))
                district_id = int(self.data.get('District'))
                self.fields['Area'].queryset = Area.objects.filter(
                    province__id=province_id, district_id=district_id).order_by('name')
                self.fields['City_Village'].queryset = CityVillage.objects.filter(
                    province__id=province_id, district_id=district_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['District'].queryset = self.instance.District.objects.all(
            ).order_by('name')
            self.fields['Province'].queryset = self.instance.Province.objects.all(
            ).order_by('name')
