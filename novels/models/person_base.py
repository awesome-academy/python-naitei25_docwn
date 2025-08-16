from django.db import models
from constants import (
    MAX_NAME_LENGTH,
    MAX_GENDER_LENGTH,
    MAX_COUNTRY_LENGTH,
    Gender,
)

class PersonBase(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    pen_name = models.CharField(
        max_length=MAX_NAME_LENGTH, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    deathday = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=MAX_GENDER_LENGTH,
        choices=Gender.choices(),
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=MAX_COUNTRY_LENGTH, null=True, blank=True
    )
    image_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
