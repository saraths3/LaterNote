import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message, Profile


class RegisterForm(UserCreationForm):
    """
    Custom registration form styled with Bootstrap 5 classes.
    """
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com (optional)'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap form-control class to all fields
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()


class UserUpdateForm(forms.ModelForm):
    """
    Form allowing users to update their name and email address.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """
    Form allowing users to update their profile bio.
    """
    class Meta:
        model = Profile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell your future self about your current dreams, principles, or favorite quote...'
            }),
        }
        labels = {
            'bio': 'About You & Your Journey'
        }


class MessageCreateForm(forms.ModelForm):
    """
    Form to create a new future message.
    Requires unlock_date to be strictly in the future.
    """
    class Meta:
        model = Message
        fields = ['title', 'category', 'content', 'unlock_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. A message to myself on graduation day'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7,
                'placeholder': 'Dear future me, today I am feeling...'
            }),
            'unlock_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'title': 'Message Title',
            'category': 'Category / Theme',
            'content': 'Message Content',
            'unlock_date': 'Unlock Date'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date attribute to tomorrow for browser datepicker
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        self.fields['unlock_date'].widget.attrs['min'] = tomorrow.isoformat()
        self.fields['category'].required = False

    def clean_category(self):
        return self.cleaned_data.get('category') or 'personal'

    def clean_unlock_date(self):
        """
        Ensure the unlock date is strictly in the future.
        """
        unlock_date = self.cleaned_data.get('unlock_date')
        if unlock_date:
            today = timezone.localdate()
            if unlock_date <= today:
                raise forms.ValidationError("The unlock date must be in the future.")
        return unlock_date


class MessageEditForm(forms.ModelForm):
    """
    Form to edit an existing message.
    Unlock date cannot be changed after creation to preserve commitment.
    """
    class Meta:
        model = Message
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7
            }),
        }
        labels = {
            'title': 'Message Title',
            'category': 'Category / Theme',
            'content': 'Message Content'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False

    def clean_category(self):
        return self.cleaned_data.get('category') or 'personal'


