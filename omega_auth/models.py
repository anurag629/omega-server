from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Custom User model with email as the unique identifier."""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    email_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False, help_text=_('Approved to use platform features'))
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class WaitingList(models.Model):
    """Model for managing users on the waiting list."""
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255)
    reason = models.TextField(blank=True, help_text=_('Reason for joining'))
    date_joined = models.DateTimeField(auto_now_add=True)
    is_invited = models.BooleanField(default=False)
    invitation_sent_at = models.DateTimeField(null=True, blank=True)
    invitation_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True, help_text=_('Token for invitation validation'))

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-date_joined']
        verbose_name = "Waiting List Entry"
        verbose_name_plural = "Waiting List Entries" 