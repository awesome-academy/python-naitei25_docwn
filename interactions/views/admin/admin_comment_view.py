from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from constants import (
    DEFAULT_PAGE_NUMBER,
    PAGINATOR_COMMON_LIST,
    PAGINATION_PAGE_RANGE
)
from common.decorators import website_admin_required
from novels.fake_data import comments

@website_admin_required
def Comments(request):
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    # For now using fake data, but should be replaced with real Comment model
    # comments_qs = Comment.objects.all().order_by('-created_at')
    
    # Add search and filtering when real model is implemented
    # if search_query:
    #     comments_qs = comments_qs.filter(
    #         Q(content__icontains=search_query) |
    #         Q(user__username__icontains=search_query) |
    #         Q(novel__name__icontains=search_query)
    #     )
    
    # if status_filter:
    #     comments_qs = comments_qs.filter(status=status_filter)
    
    # paginator = Paginator(comments_qs, PAGINATOR_COMMON_LIST)
    # page_obj = paginator.get_page(page)
    
    # Temporary pagination for fake data
    paginator = Paginator(comments, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page)
    
    return render(request, 'admin/comments_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })
