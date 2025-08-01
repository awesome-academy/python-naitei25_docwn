from django import template
from django.utils.translation import gettext_lazy as _
from constants import ApprovalStatus

register = template.Library()

@register.filter(name="status_label")
def status_label(status):
    return {
        ApprovalStatus.DRAFT.value: _("Bản nháp"),
        ApprovalStatus.PENDING.value: _("Chờ duyệt"), 
        ApprovalStatus.APPROVED.value: _("Đã duyệt"),
        ApprovalStatus.REJECTED.value: _("Bị từ chối"),
    }.get(status, "")

@register.filter(name="status_icon")
def status_icon(status):
    return {
        ApprovalStatus.DRAFT.value: "bx-edit",
        ApprovalStatus.PENDING.value: "bx-time",
        ApprovalStatus.APPROVED.value: "bx-check",
        ApprovalStatus.REJECTED.value: "bx-x",
    }.get(status, "bx-question-mark")

@register.filter(name="status_class")
def status_class(status):
    return {
        ApprovalStatus.DRAFT.value: "status-draft",
        ApprovalStatus.PENDING.value: "status-pending",
        ApprovalStatus.APPROVED.value: "status-approved", 
        ApprovalStatus.REJECTED.value: "status-rejected",
    }.get(status, "status-unknown")
