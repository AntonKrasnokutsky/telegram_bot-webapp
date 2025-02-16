from django import forms

from .models import (
    ExternalCompanies,
    ExternalTypeWorkRepairs,
    FuelCompensation,
    TypeWorkRepairs
)


class FuelCompensationForm(forms.ModelForm):
    class Meta:
        model = FuelCompensation
        fields = ['distance', 'price', ]


class TypeWorkRepairsForm(forms.ModelForm):
    class Meta:
        model = TypeWorkRepairs
        fields = ['typework', 'price', ]


# Ремонт оборудования сторонних компаний
class ExternalCompaniesForm(forms.ModelForm):
    class Meta:
        model = ExternalCompanies
        fields = ['company_name', ]


class ExternalTypeWorkRepairsForm(forms.ModelForm):
    class Meta:
        model = ExternalTypeWorkRepairs
        fields = ['typework', 'price', ]
