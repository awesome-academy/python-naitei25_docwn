from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from interactions.forms import RequestForm
from interactions.services import RequestService
from interactions.models import Request
from constants import RequestStatusChoices, RequestSortChoices, PAGINATOR_REQUEST_LIST


@login_required
@require_http_methods(["GET", "POST"])
def submit_request_view(request):
    """View để người dùng gửi yêu cầu"""
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            
            result = RequestService.create_request(
                user=request.user,
                title=title,
                content=content
            )
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect('interactions:my_requests')
            else:
                messages.error(request, result['message'])
        else:
            messages.error(request, _('Vui lòng kiểm tra lại thông tin.'))
    else:
        form = RequestForm()
    
    context = {
        'form': form,
        'page_title': _('Gửi yêu cầu hỗ trợ'),
    }
    return render(request, 'interactions/requests/submit_request.html', context)


@login_required
def my_requests_view(request):
    """View để người dùng xem danh sách yêu cầu của mình"""
    page = request.GET.get('page', 1)
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '')
    search = request.GET.get('search', '')
    
    # Validate status filter
    valid_statuses = [choice[0] for choice in RequestStatusChoices.CHOICES]
    if status_filter and status_filter not in valid_statuses:
        status_filter = None
    
    # Validate sort option
    valid_sorts = [choice[0] for choice in RequestSortChoices.CHOICES]
    if sort_by and sort_by not in valid_sorts:
        sort_by = None
    
    result = RequestService.get_user_requests(
        user=request.user,
        page=page,
        per_page=PAGINATOR_REQUEST_LIST,
        status_filter=status_filter,
        sort_by=sort_by,
        search=search.strip() if search else None
    )
    
    if not result['success']:
        messages.error(request, result['message'])
        result['requests'] = []
        result['total_count'] = 0
    
    context = {
        'requests': result.get('requests', []),
        'total_count': result.get('total_count', 0),
        'current_status_filter': status_filter,
        'current_sort': sort_by,
        'current_search': search,
        'status_choices': RequestStatusChoices.CHOICES,
        'sort_choices': RequestSortChoices.CHOICES,
        'page_title': _('Yêu cầu của tôi'),
        'has_filters': bool(status_filter or search.strip() if search else False),
        # Template text variables
        'search_placeholder': _('Tìm theo tiêu đề, nội dung...'),
        'all_status_text': _('Tất cả trạng thái'),
        'pagination_label': _('Phân trang yêu cầu'),
        'sent_at_text': _('Gửi lúc'),
        'content_truncate_length': 150,
        'date_format': 'd/m/Y H:i',
        'no_results_title': _('Không tìm thấy yêu cầu nào'),
        'no_results_with_filters_message': _('Không có yêu cầu nào phù hợp với bộ lọc hiện tại.'),
        'no_requests_title': _('Chưa có yêu cầu nào'),
        'no_requests_message': _('Bạn chưa gửi yêu cầu hỗ trợ nào.'),
        'new_request_button_text': _('Gửi yêu cầu mới'),
        'first_request_button_text': _('Gửi yêu cầu đầu tiên'),
    }
    return render(request, 'interactions/requests/my_requests.html', context)


@login_required
def request_detail_view(request, request_id):
    """View để xem chi tiết yêu cầu"""
    result = RequestService.get_request_detail(
        request_id=request_id,
        user=request.user
    )
    
    if not result['success']:
        messages.error(request, result['message'])
        return redirect('interactions:my_requests')
    
    request_obj = result['request']
    
    context = {
        'request_obj': request_obj,
        'page_title': _('Chi tiết yêu cầu'),
        # Template text variables
        'date_format': 'd/m/Y H:i',
        'admin_response_title': _('Phản hồi từ admin:'),
        'pending_note': _('Chúng tôi sẽ xem xét và phản hồi sớm nhất có thể'),
    }
    return render(request, 'interactions/requests/request_detail.html', context)
