from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    profile_picture = forms.ImageField(required=True, help_text='Required.')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


    def save(self, commit=True):
        # Save the User instance
        user = super().save(commit=commit)
        if commit:
            # Create the Profile instance and save the profile picture
            profile_picture = self.cleaned_data.get('profile_picture')
            Profile.objects.create(user=user, profile_picture=profile_picture)
        return user
    
    