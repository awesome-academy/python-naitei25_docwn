from django.db import models
from constants import (
    MAX_TAG_LENGTH,
)

class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_LENGTH, unique=True)
    slug = models.SlugField(max_length=MAX_TAG_LENGTH, unique=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name
