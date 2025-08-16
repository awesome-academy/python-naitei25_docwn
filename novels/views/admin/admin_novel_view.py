from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from novels.services import NovelService
from common.decorators import website_admin_required
from constants import (
    DATE_FORMAT_DMYHI,
    ApprovalStatus,
    PAGINATION_PAGE_RANGE,
    DEFAULT_PAGE_NUMBER,
)

@website_admin_required
def Novels(request):  
    """Admin novels list using service"""
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    page_obj = NovelService.get_admin_novels_paginated(search_query, page)
    
    return render(request, 'admin/novels_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })
    
@website_admin_required
def upload_novel_requests(request):
    """Admin pending novels list using service"""
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    page_obj = NovelService.get_pending_novels_paginated(search_query, page)

    return render(request, 'admin/request_novel_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })

@website_admin_required
def novel_detail(request, slug):
    """Admin novel detail using service"""
    novel_data = NovelService.get_admin_novel_detail(slug)
    
    if not novel_data:
        return redirect('novels:novels')

    context = {
        'novel': novel_data['novel'],
        'tags': novel_data['tags'],
        'APPROVAL_STATUS': {
            'DRAFT': ApprovalStatus.DRAFT.value,
            'PENDING': ApprovalStatus.PENDING.value,
            'APPROVED': ApprovalStatus.APPROVED.value,
            'REJECTED': ApprovalStatus.REJECTED.value,
        },
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
    }
    return render(request, 'admin/novel_detail.html', context)

@website_admin_required
def novel_request_detail(request, slug):
    """Admin pending novel detail using service"""
    novel_data = NovelService.get_pending_novel_detail(slug)
    
    if not novel_data:
        messages.warning(request, _("Yêu cầu này không còn hiệu lực."))
        return redirect('novels:upload_novel_requests')

    context = {
        'novel': novel_data['novel'],
        'tags': novel_data['tags'],
        'APPROVAL_STATUS': {
            'DRAFT': ApprovalStatus.DRAFT.value,
            'PENDING': ApprovalStatus.PENDING.value,
            'APPROVED': ApprovalStatus.APPROVED.value,
            'REJECTED': ApprovalStatus.REJECTED.value,
        },
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
    }
    return render(request, 'admin/novel_request/novel_request_detail.html', context)

@require_POST
@website_admin_required
def admin_approve_novel(request, slug):
    """Approve novel using service"""
    success = NovelService.approve_novel(slug)
    if success:
        messages.success(request, _("Tiểu thuyết đã được phê duyệt thành công."))
    else:
        messages.error(request, _("Không thể phê duyệt tiểu thuyết này."))
    
    return redirect('novels:upload_novel_requests')

@require_POST
@website_admin_required
def admin_reject_novel(request, slug):
    """Reject novel using service"""
    reason = request.POST.get('reason')
    success = NovelService.reject_novel(slug, reason)
    
    if success:
        messages.success(request, _("Tiểu thuyết đã được từ chối."))
    else:
        messages.error(request, _("Không thể từ chối tiểu thuyết này."))
    
    return redirect('novels:upload_novel_requests')
