# volunteers/forms.py

from django import forms
from .models import VolunteerRegistration

class VolunteerRegistrationForm(forms.ModelForm):
    class Meta:
        model = VolunteerRegistration
        exclude = ['event']   # 🔥 IMPORTANT (we set event in view, not form)

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your full name',
                'class': 'vreg-input'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter email',
                'class': 'vreg-input'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone number',
                'class': 'vreg-input'
            }),
            'age': forms.NumberInput(attrs={
                'placeholder': 'Your age',
                'class': 'vreg-input'
            }),
            'availability': forms.TextInput(attrs={
                'class': 'vreg-input'
            }),
            'experience': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any experience (optional)',
                'class': 'vreg-textarea'
            }),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Why do you want to volunteer?',
                'class': 'vreg-textarea'
            }),
        }