from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import Rotation


class NewEntryForm(forms.Form):
    estimated_total = forms.FloatField(min_value=1, max_value=1000000000000, required=True)


class UserCharField(forms.CharField):
    def validate(self, value):
        super().validate(value)
        if not User.objects.filter(profile__main_character__character_name=value).exists():
            raise ValidationError('Character not found')


class NewShareForm(forms.Form):
    user = UserCharField(required=True, widget=forms.TextInput(attrs={'list': 'characters'}))
    helped_setup = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'setup'}))
    share_count = forms.IntegerField(min_value=0, required=True)


NewShareFormSet = forms.formset_factory(NewShareForm, extra=0)


class NewRotationForm(forms.ModelForm):
    class Meta:
        model = Rotation
        fields = ('name', 'priority', 'tax_rate', 'max_daily_setups', 'min_people_share_setup',)


class CloseRotationForm(forms.Form):
    sales_value = forms.FloatField(min_value=1, required=True)
