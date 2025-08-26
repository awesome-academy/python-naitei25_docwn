from django import template
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def request_status_badge(request_obj):
    """
    Template filter to render request status badge with proper i18n
    Usage: {{ request_obj|request_status_badge }}
    """
    if not request_obj:
        return ""
    
    if request_obj.is_pending:
        return mark_safe(
            f'<span class="badge bg-warning text-dark">'
            f'<i class="bx bx-clock me-1"></i>'
            f'{_("Chờ xử lý")}'
            f'</span>'
        )
    else:
        return mark_safe(
            f'<span class="badge bg-success">'
            f'<i class="bx bx-check me-1"></i>'
            f'{_("Đã xử lý")}'
            f'</span>'
        )


@register.filter
def request_status_text(request_obj):
    """
    Template filter to get request status text only (without HTML)
    Usage: {{ request_obj|request_status_text }}
    """
    if not request_obj:
        return ""
    
    if request_obj.is_pending:
        return _("Chờ xử lý")
    else:
        return _("Đã xử lý")


@register.inclusion_tag('admin/interactions/includes/request_actions.html')
def request_admin_actions(request_obj, user):
    """
    Inclusion tag for admin actions on requests
    Usage: {% request_admin_actions request_obj user %}
    """
    return {
        'request_obj': request_obj,
        'user': user,
        'can_mark_processed': request_obj.is_pending if request_obj else False,
    }


@register.simple_tag
def request_processed_info(request_obj):
    """
    Simple tag to format request processed information
    Usage: {% request_processed_info request_obj %}
    """
    if not request_obj or not request_obj.is_processed or not request_obj.processed_at:
        return ""
    
    processed_text = _("Đã xử lý lúc")
    processed_by_text = _("bởi")
    
    info = f"{processed_text}: {request_obj.processed_at.strftime('%d/%m/%Y %H:%M')}"
    
    if request_obj.processed_by:
        info += f" {processed_by_text} {request_obj.processed_by.get_name()}"
    
    return info
