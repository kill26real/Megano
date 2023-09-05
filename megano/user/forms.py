from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AuthForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)


class SignUpForm(UserCreationForm):

    avatar = forms.ImageField(label='Загрузите аватар:', help_text='Аватар')
    first_name = forms.CharField(max_length=30, required=True, help_text='Имя')
    last_name = forms.CharField(max_length=30, required=True, help_text='Фамилия')
    date_of_birth = forms.DateField(required=True, help_text='Дата рождения', widget=forms.SelectDateWidget)
    city = forms.CharField(required=True, help_text='Город')
    phone_number = forms.CharField(max_length=12, required=True, help_text='Телефон')
    e_mail = forms.EmailField(required=True, help_text='Почта')


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')
