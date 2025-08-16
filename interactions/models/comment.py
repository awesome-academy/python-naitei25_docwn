from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from novels.models import Novel
from accounts.models import User
from constants import (
    MIN_LIKE_COUNT,
    DATE_FORMAT_DMY2,
)


class Comment(models.Model):
    """Bình luận của người dùng về tiểu thuyết"""
    user = models.ForeignKey(
        User, 
        on_delete=models.RESTRICT, 
        null=True, 
        blank=True,
        verbose_name=_("Người dùng"),
        related_name='comments'
    )
    novel = models.ForeignKey(
        Novel, 
        on_delete=models.RESTRICT,
        verbose_name=_("Tiểu thuyết"),
        related_name='comments'
    )
    content = models.TextField(verbose_name=_("Nội dung"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Ngày cập nhật"))
    parent_comment = models.ForeignKey(
        "self", 
        null=True, 
        blank=True, 
        on_delete=models.RESTRICT,
        verbose_name=_("Bình luận cha"),
        related_name='replies'
    )
    like_count = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(MIN_LIKE_COUNT)],
        verbose_name=_("Số lượt thích")
    )
    is_reported = models.BooleanField(default=False, verbose_name=_("Đã báo cáo"))
    is_active = models.BooleanField(default=True, verbose_name=_("Hoạt động"))

    class Meta:
        verbose_name = _("Bình luận")
        verbose_name_plural = _("Bình luận")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['novel', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['parent_comment']),
        ]

    def __str__(self):
        return f"{self.user} - {self.novel} - {self.created_at.strftime(DATE_FORMAT_DMY2)}"

    @property
    def is_reply(self):
        """Kiểm tra có phải là reply hay không"""
        return self.parent_comment is not None

    def get_replies(self):
        """Lấy tất cả replies của comment này"""
        return self.replies.filter(is_active=True).order_by('created_at')
