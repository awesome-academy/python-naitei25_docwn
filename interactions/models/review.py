from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from novels.models import Novel
from accounts.models import User
from constants import (
    MIN_RATE,
    MAX_RATE,
)

class Review(models.Model):
    """Đánh giá của người dùng về tiểu thuyết"""
    user = models.ForeignKey(
        User, 
        on_delete=models.RESTRICT,
        verbose_name=_("Người dùng"),
        related_name='reviews'
    )
    novel = models.ForeignKey(
        Novel, 
        on_delete=models.RESTRICT,
        verbose_name=_("Tiểu thuyết"),
        related_name='reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(MIN_RATE), MaxValueValidator(MAX_RATE)],
        verbose_name=_("Đánh giá"),
        help_text=_(f"Đánh giá từ {MIN_RATE}-{MAX_RATE} sao")
    )
    content = models.TextField(verbose_name=_("Nội dung"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Ngày cập nhật"))
    is_active = models.BooleanField(default=True, verbose_name=_("Hoạt động"))

    class Meta:
        verbose_name = _("Đánh giá")
        verbose_name_plural = _("Đánh giá")
        unique_together = ("user", "novel")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['novel', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.user} - {self.novel} - {self.rating}⭐"
