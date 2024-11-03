# your_app_name/forms.py
from django import forms
from django.contrib.auth.models import User

class UserBioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']  # Add any other fields you want

    bio = forms.CharField(widget=forms.Textarea, required=False, label='Bio')
