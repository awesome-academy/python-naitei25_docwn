from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from .comment import Comment
from .review import Review
from constants import (
    MAX_REASON_LENGTH,
    MAX_REPORT_STATUS_LENGTH,
    ReportReasonChoices,
    ReportStatusChoices
)

class Report(models.Model):
    """Báo cáo vi phạm"""
    user = models.ForeignKey(
        User, 
        on_delete=models.RESTRICT,
        verbose_name=_("Người báo cáo"),
        related_name='reports_made'
    )
    comment = models.ForeignKey(
        Comment, 
        null=True, 
        blank=True, 
        on_delete=models.RESTRICT,
        verbose_name=_("Bình luận bị báo cáo"),
        related_name='reports'
    )
    review = models.ForeignKey(
        Review, 
        null=True, 
        blank=True, 
        on_delete=models.RESTRICT,
        verbose_name=_("Đánh giá bị báo cáo"),
        related_name='reports'
    )
    reason = models.CharField(
        max_length=MAX_REASON_LENGTH,
        choices=ReportReasonChoices.CHOICES,
        verbose_name=_("Lý do báo cáo")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Mô tả chi tiết")
    )
    status = models.CharField(
        max_length=MAX_REPORT_STATUS_LENGTH,
        choices=ReportStatusChoices.CHOICES,
        default=ReportStatusChoices.PENDING,
        verbose_name=_("Trạng thái")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Ngày xử lý"))
    resolved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        verbose_name=_("Người xử lý"),
        related_name='reports_resolved'
    )

    class Meta:
        verbose_name = _("Báo cáo")
        verbose_name_plural = _("Báo cáo")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(comment__isnull=False) | models.Q(review__isnull=False),
                name='report_must_have_comment_or_review'
            )
        ]

    def __str__(self):
        target = self.comment or self.review
        return _(f"Báo cáo từ {self.user} - {target} - {self.get_reason_display()}")

    def resolve(self, resolved_by, description=""):
        """Xử lý báo cáo"""
        from django.utils import timezone
        
        self.status = self.ReportStatus.RESOLVED
        self.resolved_by = resolved_by
        self.resolved_at = timezone.now()
        self.description = description
        self.save(update_fields=['status', 'resolved_by', 'resolved_at', 'description'])
