from django.db import models

from constants import (
    MAX_USERNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_ROLE_LENGTH,
    MAX_NAME_LENGTH,
    MAX_IMAGE_URL_LENGTH,
    MAX_GENDER_LENGTH,
    UserRole,
    Gender,
)

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, unique=True)
    email = models.CharField(max_length=MAX_EMAIL_LENGTH, unique=True)
    password = models.CharField(max_length=MAX_PASSWORD_LENGTH)
    join_date = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)
    role = models.CharField(
        max_length=MAX_ROLE_LENGTH, choices=UserRole.choices()
    )


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True
    )
    display_name = models.CharField(
        max_length=MAX_NAME_LENGTH, null=True, blank=True
    )
    gender = models.CharField(
        max_length=MAX_GENDER_LENGTH,
        choices=Gender.choices(),
        null=True,
        blank=True,
    )
    birthday = models.DateField(null=True, blank=True)
    avatar = models.CharField(
        max_length=MAX_IMAGE_URL_LENGTH, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    interest = models.TextField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)


class OAuthProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider_name = models.CharField(max_length=MAX_NAME_LENGTH)
    provider_user_id = models.CharField(max_length=MAX_NAME_LENGTH)
