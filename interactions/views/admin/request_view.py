from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.http import require_http_methods

from interactions.forms import AdminRequestProcessForm
from interactions.services import RequestService
from interactions.models import Request
from constants import RequestStatusChoices, RequestSortChoices, PAGINATOR_ADMIN_REQUEST_LIST


@staff_member_required
def admin_request_list_view(request):
    """View để admin xem danh sách tất cả yêu cầu"""
    page = request.GET.get('page', 1)
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '')
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    user_filter = request.GET.get('user', '')
    
    # Validate status filter
    valid_statuses = [choice[0] for choice in RequestStatusChoices.CHOICES]
    if status_filter and status_filter not in valid_statuses:
        status_filter = None
    
    # Validate sort option
    valid_sorts = [choice[0] for choice in RequestSortChoices.CHOICES]
    if sort_by and sort_by not in valid_sorts:
        sort_by = None
    
    result = RequestService.get_all_requests_for_admin(
        page=page,
        per_page=PAGINATOR_ADMIN_REQUEST_LIST,
        status_filter=status_filter,
        sort_by=sort_by,
        search=search.strip() if search else None,
        date_from=date_from if date_from else None,
        date_to=date_to if date_to else None,
        user_filter=user_filter.strip() if user_filter else None
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
        'current_date_from': date_from,
        'current_date_to': date_to,
        'current_user_filter': user_filter,
        'status_choices': RequestStatusChoices.CHOICES,
        'sort_choices': RequestSortChoices.CHOICES,
        'page_title': _('Quản lý yêu cầu'),
        'has_filters': bool(status_filter or search.strip() if search else False or 
                           date_from or date_to or user_filter.strip() if user_filter else False),
        # Template text variables
        'search_placeholder': _('Tìm theo tiêu đề, nội dung, người dùng...'),
        'user_placeholder': _('Tên đăng nhập hoặc email'),
        'all_status_text': _('Tất cả'),
        'pagination_label': _('Phân trang yêu cầu'),
        'title_truncate_length': 50,
        'date_format': 'd/m/Y H:i',
        'not_processed_text': '-',
        'no_results_title': _('Không có yêu cầu nào'),
        'no_results_with_filters_message': _('Không tìm thấy yêu cầu nào với bộ lọc hiện tại.'),
        'no_requests_title': _('Không có yêu cầu nào'),
        'no_requests_message': _('Chưa có yêu cầu nào được gửi.'),
    }
    
    # Add results count text with proper pluralization
    if result.get('total_count', 0) > 0:
        context['results_count_text'] = ngettext(
            '%(count)d kết quả',
            '%(count)d kết quả',
            result.get('total_count', 0)
        ) % {'count': result.get('total_count', 0)}
    return render(request, 'admin/interactions/requests/request_list.html', context)


@staff_member_required
def admin_request_detail_view(request, request_id):
    """View để admin xem chi tiết và xử lý yêu cầu"""
    result = RequestService.get_request_detail(request_id=request_id)
    
    if not result['success']:
        messages.error(request, result['message'])
        return redirect('interactions:admin_request_list')
    
    request_obj = result['request']
    
    if request.method == 'POST':
        form = AdminRequestProcessForm(request.POST, instance=request_obj)
        if form.is_valid():
            admin_note = form.cleaned_data.get('admin_note', '')
            
            process_result = RequestService.process_request(
                request_id=request_id,
                admin_user=request.user,
                admin_note=admin_note
            )
            
            if process_result['success']:
                messages.success(request, process_result['message'])
                return redirect('interactions:admin_request_detail', request_id=request_id)
            else:
                messages.error(request, process_result['message'])
        else:
            messages.error(request, _('Vui lòng kiểm tra lại thông tin.'))
    else:
        form = AdminRequestProcessForm(instance=request_obj)
    
    context = {
        'request_obj': request_obj,
        'form': form,
        'page_title': _('Chi tiết yêu cầu'),
        # Template text variables
        'date_format': 'd/m/Y H:i',
        'date_format_short': 'd/m/Y',
        'pending_message': _('Yêu cầu này đang chờ được xử lý.'),
        'processed_message': _('Yêu cầu này đã được xử lý.'),
        'mark_processed_text': _('Đánh dấu đã xử lý'),
        'quick_process_text': _('Xử lý nhanh (không ghi chú)'),
        'quick_process_confirm': _('Bạn có chắc muốn đánh dấu yêu cầu này đã được xử lý mà không có ghi chú?'),
    }
    return render(request, 'admin/interactions/requests/request_detail.html', context)


@staff_member_required
@require_http_methods(["POST"])
def admin_mark_processed_view(request, request_id):
    """View để admin đánh dấu yêu cầu đã xử lý nhanh"""
    result = RequestService.process_request(
        request_id=request_id,
        admin_user=request.user,
        admin_note=""
    )
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])
    
    return redirect('interactions:admin_request_list')
