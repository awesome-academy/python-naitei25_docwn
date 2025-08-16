from django.db import models
from .novel import Novel
from constants import (
    MAX_NAME_LENGTH,
)

class Volume(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.RESTRICT, related_name='volumes')
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('novel', 'position'),
            ('novel', 'name')  # Prevent duplicate volume names within the same novel
        ]
        ordering = ['position']
        indexes = [
            models.Index(fields=['novel', 'position']),
            models.Index(fields=['novel', 'name']),  # Index for name lookups
        ]
        
    def __str__(self):
        return f"{self.novel.name} - {self.name}"
