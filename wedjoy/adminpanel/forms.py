# adminpanel/forms.py
from django import forms
from volunteers.models import VolunteerOpportunity


class AdminLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))



class VolunteerOpportunityForm(forms.ModelForm):
    class Meta:
        model = VolunteerOpportunity
        fields = [
            'title',
            'category',
            'description',
            'location',
            'start_date',
            'end_date',
            'required_hours',
            'cover_image'
        ]

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }