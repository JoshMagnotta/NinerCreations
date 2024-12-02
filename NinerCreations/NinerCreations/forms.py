from django import forms
from .models import Profile
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your bio...',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pop the user from kwargs
        super().__init__(*args, **kwargs)
        if user:
            # Set initial values for first and last name
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
