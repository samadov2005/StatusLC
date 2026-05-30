from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator


class Profile(models.Model):
    """Extended user profile with role and contact information."""
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('operator', 'Operator'),
        ('admin', 'Administrator'),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        null=True,
        blank=True,
        help_text="User role in the system"
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?([0-9\s\-\(\)]+)$',
                message='Enter a valid phone number.',
                code='invalid_phone'
            )
        ],
        help_text="User's phone number"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

