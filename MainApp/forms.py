from django import forms
from MainApp.models import Snippet, Comment
from MainApp.models import LANG_CHOICES, ACCESS_CHOICES
from django.contrib.auth.models import User


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['name', 'lang', 'code', 'description', 'access', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название сниппета'}),
            'lang': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Выберите язык'}),
            'code': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Код сниппета'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'access': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Приватность'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control', 'placeholder': 'Выберите теги'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].required = False

    def validate_length(self, field_name, min_len, max_len):
        value = self.cleaned_data.get(field_name, '')
        if len(value) < min_len:
            raise forms.ValidationError(f"минимальная длина {min_len} символа")
        elif len(value) > max_len:
            raise forms.ValidationError(f"максимальная длина {max_len} символов")
        return value

    def clean_name(self):
        return self.validate_length('name',3,20)

    def clean_code(self):
        return self.validate_length('code',3,1000)



class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
        }

    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Пароль'}
    ))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}
    ))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 == password2:
            return password2
        raise forms.ValidationError('Пароли не совпадают')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите ваш комментарий здесь...'}),
        }
