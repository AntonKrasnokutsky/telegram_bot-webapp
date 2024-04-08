from django import forms

from .models import FuelCompensation, TypeWorkRepairs


class FuelCompensationForm(forms.ModelForm):
    class Meta:
        model = FuelCompensation
        fields = ['distance', 'price', ]


class TypeWorkRepairsForm(forms.ModelForm):
    class Meta:
        model = TypeWorkRepairs
        fields = ['typework', 'price', ]
