from django import forms


class NewEntryForm(forms.Form):
    estimated_total = forms.FloatField(min_value=1, required=True)


class NewShareForm(forms.Form):
    user = forms.CharField(required=True)
    helped_setup = forms.BooleanField()
    share_count = forms.IntegerField(min_value=0, required=True)


NewShareFormSet = forms.formset_factory(NewShareForm, extra=1)
