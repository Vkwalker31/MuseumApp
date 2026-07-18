"""
Формы музея с валидацией на стороне сервера.
"""
from django import forms
from .models import Exhibit, TicketPurchase, TicketPrice, Tour, Visitor
from pages.models import PromoCode


class ExhibitForm(forms.ModelForm):
    class Meta:
        model = Exhibit
        fields = [
            'name', 'art_type', 'date_of_entry', 'hall', 'guardian',
            'description', 'image',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_entry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class TicketBuyForm(forms.Form):
    """Покупка билета посетителем."""
    tour = forms.ModelChoiceField(
        queryset=Tour.objects.all().order_by('-date'),
        required=False,
        label='Экскурсия',
        empty_label='Без экскурсии (общий вход)',
    )
    ticket_price = forms.ModelChoiceField(
        queryset=TicketPrice.objects.all().order_by('name'),
        label='Тариф',
    )
    promo_code = forms.CharField(
        max_length=50,
        required=False,
        label='Промокод',
        widget=forms.TextInput(attrs={'placeholder': 'WELCOME10'}),
    )

    def clean_promo_code(self):
        code = (self.cleaned_data.get('promo_code') or '').strip()
        if not code:
            return ''
        promo = PromoCode.objects.filter(code__iexact=code, is_active=True).first()
        if not promo:
            raise forms.ValidationError('Промокод не найден или недействителен.')
        return promo.code

    def calculate_price(self):
        """Цена с учётом промокода."""
        tp = self.cleaned_data['ticket_price']
        price = tp.base_price
        code = self.cleaned_data.get('promo_code')
        if code:
            promo = PromoCode.objects.filter(code__iexact=code, is_active=True).first()
            if promo:
                if promo.discount_percent:
                    price = price * (1 - promo.discount_percent / 100)
                elif promo.discount_amount:
                    price = max(price - promo.discount_amount, 0)
        return price


class VisitorProfileForm(forms.ModelForm):
    """Профиль посетителя: ФИО, дата рождения (18+), телефон."""
    class Meta:
        model = Visitor
        fields = ['full_name', 'birth_date', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'required': True, 'placeholder': 'ФИО'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'phone': forms.TextInput(attrs={
                'required': True,
                'placeholder': '+375 (29) XXX-XX-XX',
                'pattern': r'\+375\s?\((25|29|33|44)\)\s?\d{3}-\d{2}-\d{2}',
                'title': 'Формат: +375 (29) XXX-XX-XX',
            }),
        }

    def clean(self):
        cleaned = super().clean()
        instance = Visitor(
            full_name=cleaned.get('full_name') or '',
            birth_date=cleaned.get('birth_date'),
            phone=cleaned.get('phone') or '',
        )
        instance.clean()
        return cleaned
