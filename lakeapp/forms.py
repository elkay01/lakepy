from lakeapp.models import Shopcart
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from django import forms


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields=('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
        widgets = {
             'first_name':forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}),
             'last_name':forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}),
             'username':forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}),
             'email':forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}),
             'password1':forms.PasswordInput(attrs={'class':'form-control'}),
             'password2':forms.PasswordInput(attrs={'class':'form-control'}),
        }


class ShopCartForm(forms.ModelForm):
    class Meta:
        models=Shopcart
        fields=('quantity',)