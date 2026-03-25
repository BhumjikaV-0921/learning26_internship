from django import forms
from business.models import Business
from events.models import Event
from core.models import User

class addBusiness(forms.ModelForm):
    class Meta:
        model = Business
        exclude = ['owner', 'approval_status', 'created_at']  # exclude owner and system fields

        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Golden Crust Bakery'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Select category'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'hello@business.com'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell the community about your business...'
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123 Main Street'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP Code'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Longitude'
            }),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            # Optional: add widgets for business hours
            'monday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'monday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'tuesday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'tuesday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'wednesday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'wednesday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'thursday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'thursday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'friday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'friday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'saturday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'saturday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'sunday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'sunday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
    
class OwnerProfileUpdateForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(),required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(),required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(),required=False)
    
    class Meta:
        model = User
        fields = [
            'firstName',
            'lastName',
            'phone_number',
            'email',
            'gender',
            'address',
            'city',
            'state',
        ]

        widgets = {
            'gender': forms.RadioSelect(),
        }
    
class EventProfileUpdateForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(),required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(),required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(),required=False)
    
    class Meta:
        model = User
        fields = [
            'firstName',
            'lastName',
            'phone_number',
            'email',
            'gender',
            'address',
            'city',
            'state',
        ]

        widgets = {
            'gender': forms.RadioSelect(),
        }
    


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            "title",
            "category",
            "description",
            "event_date",
            "start_time",
            "end_time",
            "location_name",
            "address",
            "latitude",
            "longitude",
            "max_participants",
            "registration_fee",
            "cover_image",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Community Yoga in the Park"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "location_name": forms.TextInput(),
            "address": forms.TextInput(),
            "latitude": forms.NumberInput(),
            "longitude": forms.NumberInput(),
            "max_participants": forms.NumberInput(),
            "registration_fee": forms.NumberInput(),
        }