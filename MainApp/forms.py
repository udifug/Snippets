from django import forms

class SnippetForm(forms.Form):
    name = forms.CharField(
        label="Название сниппета",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Краткое название'}),
    )

    lang = forms.ChoiceField(
        label="Язык программирования",
        choices=[
            ('', '--- Выберите язык ---'),
            ("python", "Python"),
            ("cpp", "C++"),
            ("java", "Java"),
            ("javascript", "JavaScript")
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    code = forms.CharField(
        label="Исходный код",
        max_length=5000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Введите ваш код здесь'})
    )