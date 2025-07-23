from django import forms
from MainApp.models import Snippet
from MainApp.models import LANG_CHOICES


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['name', 'lang', 'code', 'description', 'access']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название сниппета'}),
            'lang': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Выберите язык'}),
            'code': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Код сниппета'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'access': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Приватность'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError("Название должно содержать не менее 3 символов.")
        return name
