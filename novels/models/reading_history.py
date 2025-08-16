from django.db import models
from accounts.models import User
from .novel import Novel
from .chapter import Chapter
from constants import (
    PROGRESS_DEFAULT,
)

class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='reading_history')
    chapter = models.ForeignKey(Chapter, on_delete=models.RESTRICT, related_name='reading_history')
    novel = models.ForeignKey(Novel, on_delete=models.RESTRICT, related_name='reading_history')
    read_at = models.DateTimeField(auto_now_add=True)
    reading_progress = models.FloatField(default=PROGRESS_DEFAULT)

    class Meta:
        unique_together = ('user', 'chapter')
        indexes = [
            models.Index(fields=['user', '-read_at']),
            models.Index(fields=['user', 'novel', '-read_at']),
            models.Index(fields=['chapter']),
        ]
