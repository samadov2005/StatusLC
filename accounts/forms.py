from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator


class StudentSignUpForm(UserCreationForm):
    """Form for student registration with validation."""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required.'
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional.'
    )
    email = forms.EmailField(
        required=True,
        help_text='Required. We\'ll send confirmation emails here.'
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?([0-9\s\-\(\)]+)$',
                message='Enter a valid phone number.',
                code='invalid_phone'
            )
        ],
        help_text='Optional. Format: +998 XX XXX XXXX or similar.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_username(self):
        """Ensure username is unique and valid."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

