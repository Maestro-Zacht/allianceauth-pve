from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from allianceauth.services.hooks import get_extension_logger

from .models import Rotation

logger = get_extension_logger(__name__)


class NewEntryForm(forms.Form):
    estimated_total = forms.FloatField(min_value=1, max_value=1000000000000, required=True, widget=forms.NumberInput(attrs={'style': 'width: 70%'}))


class UserPkField(forms.IntegerField):
    def validate(self, value):
        super().validate(value)
        if not User.objects.filter(pk=value).exists():
            logger.error(f"User with pk {value} not found!")
            raise ValidationError('Character not found')


class NewShareForm(forms.Form):
    user = UserPkField(required=True, widget=forms.TextInput(attrs={'style': 'display: none;', 'class': 'user-pk-list'}))
    helped_setup = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'setup'}))
    share_count = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={'style': 'width: 10ch;'}))


NewShareFormSet = forms.formset_factory(NewShareForm, extra=0)


class NewRotationForm(forms.ModelForm):
    class Meta:
        model = Rotation
        fields = ('name', 'priority', 'tax_rate', 'max_daily_setups', 'min_people_share_setup',)


class CloseRotationForm(forms.Form):
    sales_value = forms.FloatField(min_value=1, required=True)
