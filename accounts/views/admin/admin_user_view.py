from django.shortcuts import render
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import User
from constants import (
    DEFAULT_PAGE_NUMBER,
    PAGINATOR_COMMON_LIST,
    PAGINATION_PAGE_RANGE,
    DATE_FORMAT_DMY,
    UserRole
)
from common.decorators import website_admin_required

@website_admin_required
def Users(request):
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    users = User.objects.filter(role=UserRole.USER.value).order_by('-date_joined')
    
    # Add search functionality
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(users, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page)

    return render(request, 'admin/users_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })
