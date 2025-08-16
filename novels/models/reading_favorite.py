from django.db import models
from accounts.models import User
from .novel import Novel

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='favorites')
    novel = models.ForeignKey(Novel, on_delete=models.RESTRICT, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'novel')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['novel']),
        ]
