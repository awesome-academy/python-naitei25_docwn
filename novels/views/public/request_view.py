from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from novels.models import AuthorRequest, ArtistRequest
from novels.forms import AuthorRequestForm, ArtistRequestForm
from novels.services import RequestService
from constants import (
    ApprovalStatus, 
    Gender,
    PAGINATOR_COMMON_LIST,
)

@login_required
def author_request_create(request):
    """Create a new author request"""
    if request.method == 'POST':
        form = AuthorRequestForm(request.POST)
        if form.is_valid():
            author_request = RequestService.create_author_request_from_form(form, request.user)
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': _('Yêu cầu tạo tác giả đã được gửi thành công!'),
                    'request_id': author_request.id,
                    'request_name': author_request.get_display_name()
                })
            
            messages.success(request, _('Yêu cầu tạo tác giả đã được gửi thành công!'))
            return redirect('novels:author_request_list')
        else:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = AuthorRequestForm()
    
    return render(request, 'novels/requests/author_request_form.html', {
        'form': form,
        'title': _('Yêu cầu tạo tác giả mới'),
        'submit_text': _('Gửi yêu cầu')
    })

@login_required
def artist_request_create(request):
    """Create a new artist request"""
    if request.method == 'POST':
        form = ArtistRequestForm(request.POST)
        if form.is_valid():
            artist_request = RequestService.create_artist_request_from_form(form, request.user)
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': _('Yêu cầu tạo họa sĩ đã được gửi thành công!'),
                    'request_id': artist_request.id,
                    'request_name': artist_request.get_display_name()
                })
            
            messages.success(request, _('Yêu cầu tạo họa sĩ đã được gửi thành công!'))
            return redirect('novels:artist_request_list')
        else:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = ArtistRequestForm()
    
    return render(request, 'novels/requests/artist_request_form.html', {
        'form': form,
        'title': _('Yêu cầu tạo họa sĩ mới'),
        'submit_text': _('Gửi yêu cầu')
    })

@login_required
def author_request_list(request):
    """List user's author requests with filters + search"""
    page_number = request.GET.get('page')
    status = request.GET.get('status')
    gender = request.GET.get('gender')
    search = request.GET.get('search')

    qs = AuthorRequest.objects.filter(created_by=request.user).order_by("-created_at")

    if status:
        qs = qs.filter(approval_status=status)
    if gender:
        qs = qs.filter(gender=gender)
    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(pen_name__icontains=search)

    paginator = Paginator(qs, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page_number)

    return render(request, 'novels/requests/author_request_list.html', {
        'page_obj': page_obj,
        'title': _('Yêu cầu thêm tác giả của tôi'),
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        'MALE': Gender.MALE.value,
        'FEMALE': Gender.FEMALE.value,
        'current_status': status,
        'current_gender': gender,
        'current_search': search,
    })


@login_required
def artist_request_list(request):
    """List user's artist requests with filters + search"""
    page_number = request.GET.get('page')
    status = request.GET.get('status')
    gender = request.GET.get('gender')
    search = request.GET.get('search')

    qs = ArtistRequest.objects.filter(created_by=request.user).order_by("-created_at")

    if status:
        qs = qs.filter(approval_status=status)
    if gender:
        qs = qs.filter(gender=gender)
    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(pen_name__icontains=search)

    paginator = Paginator(qs, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page_number)

    return render(request, 'novels/requests/artist_request_list.html', {
        'page_obj': page_obj,
        'title': _('Yêu cầu thêm họa sĩ của tôi'),
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        'MALE': Gender.MALE.value,
        'FEMALE': Gender.FEMALE.value,
        'current_status': status,
        'current_gender': gender,
        'current_search': search,
    })

@login_required
def author_request_detail(request, pk):
    """View author request detail"""
    author_request = RequestService.get_user_author_request(pk, request.user)
    
    return render(request, 'novels/requests/author_request_detail.html', {
        'request': author_request,
        'title': f"yêu cầu thêm tác giả: {author_request.get_display_name()}",
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        'MALE': Gender.MALE.value,
        'FEMALE': Gender.FEMALE.value,
    })

@login_required
def artist_request_detail(request, pk):
    """View artist request detail"""
    artist_request = RequestService.get_user_artist_request(pk, request.user)
    
    return render(request, 'novels/requests/artist_request_detail.html', {
        'request': artist_request,
        'title': f"yêu cầu thêm họa sĩ: {artist_request.get_display_name()}",
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        'MALE': Gender.MALE.value,
        'FEMALE': Gender.FEMALE.value,
    })
