from django.db import models
from django.utils.translation import gettext_lazy as _

from novels.models import Novel
from accounts.models import User
from .comment import Comment
from .review import Review
from constants import (
    MAX_TYPE_LENGTH,
    MAX_TITLE_LENGTH,
    DATE_FORMAT_DMY2,
    NotificationTypeChoices,
)

class Notification(models.Model):
    """Thông báo cho người dùng"""
    user = models.ForeignKey(
        User, 
        on_delete=models.RESTRICT,
        verbose_name=_("Người dùng"),
        related_name='notifications'
    )
    type = models.CharField(
        max_length=MAX_TYPE_LENGTH,
        choices=NotificationTypeChoices.CHOICES,
        verbose_name=_("Loại thông báo")
    )
    title = models.CharField(max_length=MAX_TITLE_LENGTH, verbose_name=_("Tiêu đề"))
    content = models.TextField(verbose_name=_("Nội dung"))
    is_read = models.BooleanField(default=False, verbose_name=_("Đã đọc"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo"))
    
    # Các trường tham chiếu để biết thông báo liên quan đến đối tượng nào
    related_comment = models.ForeignKey(
        Comment,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Bình luận liên quan")
    )
    related_review = models.ForeignKey(
        Review,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Đánh giá liên quan")
    )
    related_novel = models.ForeignKey(
        Novel,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Tiểu thuyết liên quan")
    )

    class Meta:
        verbose_name = _("Thông báo")
        verbose_name_plural = _("Thông báo")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_type_display()} - {self.created_at.strftime(DATE_FORMAT_DMY2)}"

    def mark_as_read(self):
        """Đánh dấu thông báo là đã đọc"""
        self.is_read = True
        self.save(update_fields=['is_read'])
