"""
Формы страниц с серверной валидацией.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Review
from museum.models import Visitor, validate_phone, validate_age_18

User = get_user_model()


class ReviewForm(forms.ModelForm):
    """Форма отзыва: текст, оценка. Имя подставится из user."""
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Текст отзыва',
                'required': True,
                'minlength': 3,
            }),
        }


class RegisterForm(UserCreationForm):
    """Регистрация посетителя с профилем (18+, телефон)."""
    full_name = forms.CharField(max_length=200, label='ФИО', required=True)
    birth_date = forms.DateField(
        label='Дата рождения',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'required': True}),
    )
    phone = forms.CharField(
        max_length=25,
        label='Телефон',
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '+375 (29) XXX-XX-XX',
            'pattern': r'\+375\s?\((25|29|33|44)\)\s?\d{3}-\d{2}-\d{2}',
            'title': 'Формат: +375 (29) XXX-XX-XX',
            'required': True,
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'full_name', 'birth_date', 'phone', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        validate_phone(phone)
        return phone

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        validate_age_18(birth_date)
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Visitor.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                birth_date=self.cleaned_data['birth_date'],
                phone=self.cleaned_data['phone'],
            )
        return user
