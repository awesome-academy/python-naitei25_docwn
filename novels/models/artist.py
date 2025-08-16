from django.db import models
from .person_base import PersonBase

class Artist(PersonBase):
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]
