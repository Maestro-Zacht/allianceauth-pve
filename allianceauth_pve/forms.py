from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from allianceauth.services.hooks import get_extension_logger
from allianceauth.eveonline.models import EveCharacter
from allianceauth.authentication.models import CharacterOwnership

from .models import Rotation

logger = get_extension_logger(__name__)


class NewEntryForm(forms.Form):
    estimated_total = forms.FloatField(min_value=1, max_value=1000000000000, initial=0, required=True, widget=forms.NumberInput(attrs={'style': 'width: 50%'}))


class NewRoleForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput())
    value = forms.IntegerField(min_value=1)


class NewRoleFormset(forms.BaseFormSet):
    def clean(self):
        if not any(self.errors):
            names = set()
            for form in self.forms:
                name = form.cleaned_data.get('name')
                if name in names:
                    raise ValidationError('Roles must have different names!')
                names.add(name)


NewRoleFormSet = forms.formset_factory(NewRoleForm, formset=NewRoleFormset, extra=0, min_num=1, validate_min=True)


class UserPkField(forms.IntegerField):
    def validate(self, value):
        super().validate(value)
        if not User.objects.filter(pk=value).exists():
            logger.error(f"User with pk {value} not found!")
            raise ValidationError('User not found')


class CharacterPkField(forms.IntegerField):
    def validate(self, value):
        super().validate(value)
        if not EveCharacter.objects.filter(pk=value).exists():
            logger.error(f"Character with pk {value} not found!")
            raise ValidationError('Character not found')


class NewShareForm(forms.Form):
    user = UserPkField(required=True, widget=forms.TextInput(attrs={'style': 'display: none;', 'class': 'user-pk-list'}))
    character = CharacterPkField(required=True, widget=forms.TextInput(attrs={'style': 'display: none;', 'class': 'character-pk-list'}))
    helped_setup = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'setup'}))
    site_count = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={'style': 'width: 10ch;'}))
    role = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-control', 'style': 'height: auto;'}))


class NewShareFormset(forms.BaseFormSet):
    def clean(self):
        if not any(self.errors):
            characters = set()
            for form in self.forms:
                char = form.cleaned_data.get('character')
                user = form.cleaned_data.get('user')
                if char in characters:
                    raise ValidationError('Only 1 share per character!')

                if not CharacterOwnership.objects.filter(character_id=char, user_id=user).exists():
                    raise ValidationError('Character ownership wrong!')

                characters.add(char)


NewShareFormSet = forms.formset_factory(NewShareForm, formset=NewShareFormset, extra=0)


class NewRotationForm(forms.ModelForm):
    class Meta:
        model = Rotation
        fields = ('name', 'priority', 'tax_rate', 'max_daily_setups', 'min_people_share_setup',)


class CloseRotationForm(forms.Form):
    sales_value = forms.FloatField(min_value=1, required=True)
