from django import forms
from django.contrib.auth.models import User

class OrderForm(forms.Form):

    message = forms.CharField(widget=forms.Textarea)