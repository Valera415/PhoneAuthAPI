from django import forms
from django.core.validators import RegexValidator


phone_validator = RegexValidator(regex=r'^\d{10}$', message='Номер должен состоять из 10 цифр, без ключевой +7 или 8')


class RegistrationForm(forms.Form):
    phone_number = forms.CharField(label='Номер телефона', max_length=10, validators=[phone_validator])


class AuthorizationForm(forms.Form):
    authorization_code = forms.CharField(label='Код из СМС', max_length=6)


class ReferralCodeForm(forms.Form):
    referral_code = forms.CharField(label='Код друга', max_length=6)

