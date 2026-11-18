import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message


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


class MessageCreateForm(forms.ModelForm):
    """
    Form to create a new future message.
    Requires unlock_date to be strictly in the future.
    """
    class Meta:
        model = Message
        fields = ['title', 'content', 'unlock_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. A message to myself on graduation day'
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
            'content': 'Message Content',
            'unlock_date': 'Unlock Date'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date attribute to tomorrow for browser datepicker
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        self.fields['unlock_date'].widget.attrs['min'] = tomorrow.isoformat()

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
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7
            }),
        }
        labels = {
            'title': 'Message Title',
            'content': 'Message Content'
        }
