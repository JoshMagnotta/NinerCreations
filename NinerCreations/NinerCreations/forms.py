from django import forms
from .models import Profile
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your new email',
            }),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']