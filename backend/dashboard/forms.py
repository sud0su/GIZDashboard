from django import forms
from .models import Undss
from django_select2.forms import Select2Widget
from bootstrap_datepicker_plus import DateTimePickerInput, TimePickerInput

class UndssForm(forms.ModelForm):
    
    class Meta:
        model = Undss
        fields = '__all__'
        widgets = {
            'Date': DateTimePickerInput(), 
            'Time_of_Incident': TimePickerInput(),
            'Province': Select2Widget,
            'District': Select2Widget,
            'City_Village': Select2Widget,
            'Area': Select2Widget,
            'Incident_Type': Select2Widget,
            'Incident_Subtype': Select2Widget,
            'Initiator': Select2Widget,
            'Target': Select2Widget,
        }
        # fields = ("",)
