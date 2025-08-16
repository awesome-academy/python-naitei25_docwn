from django.db import models
from .person_base import PersonBase

class Author(PersonBase):
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]
