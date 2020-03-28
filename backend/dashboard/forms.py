from django import forms
from .models import Undss

class UndssForm(forms.ModelForm):
    
    class Meta:
        model = Undss
        fields = '__all__'
        # fields = ("",)
