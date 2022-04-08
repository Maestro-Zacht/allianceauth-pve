from django import forms

from .models import Entry, EntryCharacter


# class EntryCharacterForm(forms.ModelForm):
#     class Meta:
#         model = EntryCharacter
#         fields = ('share_count', 'character', 'helped_setup',)


# class EntryForm(forms.ModelForm):
#     class Meta:
#         model = Entry
#         fields = ('shares', 'estimated_total',)

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['shares'].required = True
#         data = kwargs.get('data')

#         self.shares_form = forms.modelformset_factory(EntryCharacter)

#     def clean(self):
#         if not self.house_form.is_valid():

#         return super().clean()
