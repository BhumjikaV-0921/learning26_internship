from django import forms
from django.contrib.auth import get_user_model
from .models import OTP

User = get_user_model()

class SendOTPForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    otp_type = forms.ChoiceField(
        choices=OTP.OTP_TYPES,
        widget=forms.HiddenInput(),
        initial='registration'
    )

class VerifyOTPForm(forms.Form):
    email = forms.EmailField(
        widget=forms.HiddenInput()
    )
    otp_code = forms.CharField(
        max_length=6,
        label="OTP Code",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'maxlength': '6'
        })
    )
    otp_type = forms.ChoiceField(
        choices=OTP.OTP_TYPES,
        widget=forms.HiddenInput()
    )

class UserRegistrationWithOTPForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'role', 'phone_number', 'profileImage']
        widgets = {
            'firstName': forms.TextInput(attrs={'class': 'form-control'}),
            'lastName': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profileImage': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user