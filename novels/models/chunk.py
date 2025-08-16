from django.db import models
from .chapter import Chapter
from constants import (
    COUNT_DEFAULT,
)

class Chunk(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.RESTRICT, related_name='chunks')
    position = models.IntegerField()
    content = models.TextField()
    word_count = models.IntegerField(default=COUNT_DEFAULT)
    
    class Meta:
        unique_together = ('chapter', 'position')
        ordering = ['position']
        indexes = [
            models.Index(fields=['chapter', 'position']),
        ]
        
    def __str__(self):
        return f"{self.chapter.title} - Chunk {self.position}"
