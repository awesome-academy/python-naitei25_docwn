from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction

from novels.models import AuthorRequest, ArtistRequest, Author, Artist
from novels.forms import AuthorRequestForm, ArtistRequestForm
from novels.services import AdminRequestService
from constants import (
    ApprovalStatus, 
    Gender,
    PAGINATOR_COMMON_LIST,
    MAX_TRUNCATED_PERSON_DESCRIPTION_LENGTH,
)
from common.decorators import website_admin_required

@website_admin_required
def author_request_admin_list(request):
    """Admin view for author requests"""
    status_filter = request.GET.get('status', '')
    page_number = request.GET.get('page')
    search_query = request.GET.get('search', '')
    creator = request.GET.get('creator', '')
    page_obj = AdminRequestService.get_all_author_requests(
        status_filter, page_number, search_query, creator
    )
    context = {
        'page_obj': page_obj,
        'title': _('Quản lý yêu cầu thêm tác giả'),
        'status_filter': status_filter,
        'search_query': search_query,
        'creator': creator,
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        'MALE': Gender.MALE.value,
        'FEMALE': Gender.FEMALE.value,
    }
    return render(request, 'admin/requests/author_request_list.html', context)

@website_admin_required
def artist_request_admin_list(request):
    """Admin view for artist requests"""
    status_filter = request.GET.get('status', '')
    page_number = request.GET.get('page')
    search_query = request.GET.get('search', '')
    creator = request.GET.get('creator', '')
    page_obj = AdminRequestService.get_all_artist_requests(
        status_filter, page_number, search_query, creator
    )
    context = {
        'page_obj': page_obj,
        'title': _('Quản lý yêu cầu thêm họa sĩ'),
        'status_filter': status_filter,
        'search_query': search_query,
        'creator': creator,
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        'MALE': Gender.MALE.value,
        'FEMALE': Gender.FEMALE.value,
    }
    return render(request, 'admin/requests/artist_request_list.html', context)

@website_admin_required
def author_request_admin_detail(request, pk):
    """Admin view for author request detail"""
    author_request = AdminRequestService.get_author_request(pk)
    
    context = {
        'request': author_request,
        'title': f"Chi tiết yêu cầu thêm tác giả: {author_request.get_display_name()}",
        'novels_using_request': author_request.novels.all(),
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        'MALE': Gender.MALE.value,
        'FEMALE': Gender.FEMALE.value,
    }
    
    return render(request, 'admin/requests/author_request_detail.html', context)

@website_admin_required
def artist_request_admin_detail(request, pk):
    """Admin view for artist request detail"""
    artist_request = AdminRequestService.get_artist_request(pk)
    
    context = {
        'request': artist_request,
        'title': f"Chi tiết yêu cầu thêm họa sĩ: {artist_request.get_display_name()}",
        'novels_using_request': artist_request.novels.all(),
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        'MALE': Gender.MALE.value,
        'FEMALE': Gender.FEMALE.value,
    }
    
    return render(request, 'admin/requests/artist_request_detail.html', context)

@website_admin_required
def approve_author_request(request, pk):
    """Approve an author request"""
    author_request = AdminRequestService.get_author_request(pk)
    
    if author_request.approval_status == ApprovalStatus.APPROVED.value:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': False, 'message': _('Yêu cầu đã được duyệt trước đó.')})
        messages.warning(request, _('Yêu cầu đã được duyệt trước đó.'))
        return redirect('admin:author_request_detail', pk=pk)
    
    if request.method == 'POST':
        result = AdminRequestService.approve_author_request(pk, request.user)
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse(result)
        
        if result['success']:
            messages.success(request, _(result['message']))
        else:
            messages.error(request, _(result['message']))
        
        return redirect('admin:author_request_detail', pk=pk)
    
    return render(request, 'admin/requests/approve_author_request.html', {
        'request': author_request,
        'title': f"Duyệt yêu cầu thêm tác giả: {author_request.get_display_name()}",
        'MAX_TRUNCATED_PERSON_DESCRIPTION_LENGTH': MAX_TRUNCATED_PERSON_DESCRIPTION_LENGTH
    })

@website_admin_required
def approve_artist_request(request, pk):
    """Approve an artist request"""
    artist_request = AdminRequestService.get_artist_request(pk)
    
    if artist_request.approval_status == ApprovalStatus.APPROVED.value:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': False, 'message': _('Yêu cầu đã được duyệt trước đó.')})
        messages.warning(request, _('Yêu cầu đã được duyệt trước đó.'))
        return redirect('admin:artist_request_detail', pk=pk)
    
    if request.method == 'POST':
        result = AdminRequestService.approve_artist_request(pk, request.user)
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse(result)
        
        if result['success']:
            messages.success(request, _(result['message']))
        else:
            messages.error(request, _(result['message']))
        
        return redirect('admin:artist_request_detail', pk=pk)
    
    return render(request, 'admin/requests/approve_artist_request.html', {
        'request': artist_request,
        'title': f"Duyệt yêu cầu thêm họa sĩ: {artist_request.get_display_name()}",
        'MAX_TRUNCATED_PERSON_DESCRIPTION_LENGTH': MAX_TRUNCATED_PERSON_DESCRIPTION_LENGTH
    })

@website_admin_required
def reject_author_request(request, pk):
    """Reject an author request"""
    author_request = AdminRequestService.get_author_request(pk)
    
    if request.method == 'POST':
        rejected_reason = request.POST.get('rejected_reason', '').strip()
        result = AdminRequestService.reject_author_request(pk, rejected_reason)
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse(result)
        
        if result['success']:
            messages.success(request, _(result['message']))
        else:
            messages.error(request, _(result['message']))
        
        return redirect('admin:author_request_detail', pk=pk)
    
    return render(request, 'admin/requests/reject_author_request.html', {
        'request': author_request,
        'title': f"Từ chối yêu cầu thêm tác giả: {author_request.get_display_name()}"
    })

@website_admin_required
def reject_artist_request(request, pk):
    """Reject an artist request"""
    artist_request = AdminRequestService.get_artist_request(pk)
    
    if request.method == 'POST':
        rejected_reason = request.POST.get('rejected_reason', '').strip()
        result = AdminRequestService.reject_artist_request(pk, rejected_reason)
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse(result)
        
        if result['success']:
            messages.success(request, _(result['message']))
        else:
            messages.error(request, _(result['message']))
        
        return redirect('admin:artist_request_detail', pk=pk)
    
    return render(request, 'admin/requests/reject_artist_request.html', {
        'request': artist_request,
        'title': f"Từ chối yêu cầu thêm họa sĩ: {artist_request.get_display_name()}"
    })
