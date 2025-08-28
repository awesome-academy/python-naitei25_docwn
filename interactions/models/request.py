from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from accounts.models import User
from constants import (
    MAX_REQUEST_TITLE_LENGTH,
    MAX_REQUEST_STATUS_LENGTH,
    RequestStatusChoices
)


class Request(models.Model):
    """Yêu cầu/phản hồi từ người dùng"""
    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        verbose_name=_("Người gửi"),
        related_name='requests_sent'
    )
    title = models.CharField(
        max_length=MAX_REQUEST_TITLE_LENGTH,
        verbose_name=_("Tiêu đề")
    )
    content = models.TextField(
        verbose_name=_("Nội dung")
    )
    status = models.CharField(
        max_length=MAX_REQUEST_STATUS_LENGTH,
        choices=RequestStatusChoices.CHOICES,
        default=RequestStatusChoices.PENDING,
        verbose_name=_("Trạng thái")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Ngày tạo")
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Ngày xử lý")
    )
    processed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        verbose_name=_("Người xử lý"),
        related_name='requests_processed'
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name=_("Ghi chú admin")
    )

    class Meta:
        verbose_name = _("Yêu cầu")
        verbose_name_plural = _("Yêu cầu")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Yêu cầu từ {self.user} - {self.title}"

    def mark_processed(self, processed_by, admin_note=""):
        """Đánh dấu yêu cầu đã được xử lý"""
        self.status = RequestStatusChoices.PROCESSED
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        self.admin_note = admin_note
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'admin_note'])

    @property
    def is_pending(self):
        """Kiểm tra yêu cầu đang chờ xử lý"""
        return self.status == RequestStatusChoices.PENDING

    @property
    def is_processed(self):
        """Kiểm tra yêu cầu đã được xử lý"""
        return self.status == RequestStatusChoices.PROCESSED
