from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from constants import (
    MAX_NAME_LENGTH,
    MAX_GENDER_LENGTH,
    MAX_COUNTRY_LENGTH,
    ApprovalStatus,
    Gender,
)

class AuthorRequest(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    pen_name = models.CharField(
        max_length=MAX_NAME_LENGTH, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    deathday = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=MAX_GENDER_LENGTH,
        choices=Gender.choices(),
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=MAX_COUNTRY_LENGTH, null=True, blank=True
    )
    image_url = models.TextField(null=True, blank=True)
    
    # Request specific fields
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author_requests'
    )
    approval_status = models.CharField(
        max_length=1,
        choices=ApprovalStatus.choices(),
        default=ApprovalStatus.PENDING.value,
        db_index=True,
    )
    rejected_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_author_requests'
    )
    
    # Reference to the created author if approved
    created_author = models.OneToOneField(
        'Author',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_request'
    )

    class Meta:
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['approval_status', '-created_at']),
            models.Index(fields=['name']),
        ]
        verbose_name = _("Author Request")
        verbose_name_plural = _("Author Requests")

    def __str__(self):
        return f"Author Request: {self.name} by {self.created_by.username}"

    def get_display_name(self):
        """Get the display name (pen_name if available, otherwise name)"""
        return self.pen_name if self.pen_name else self.name

    def can_be_used_in_novel(self):
        """Check if this request can be used in a novel (pending or approved)"""
        return self.approval_status in [ApprovalStatus.PENDING.value, ApprovalStatus.APPROVED.value]
