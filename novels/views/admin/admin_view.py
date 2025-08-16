from django.shortcuts import render
from novels.models import Chapter, Novel
from django.utils.translation import gettext as _
from accounts.models import User
from constants import (
    ApprovalStatus,
    UserRole,
)
from common.decorators import website_admin_required
from novels.fake_data import getNewNovels, top_novels_this_month, new_novels,authors

@website_admin_required
def Admin(request):
    total_users = User.objects.filter(role = UserRole.USER.value).count()
    total_novels = Novel.objects.count()

    approved_novels = Novel.objects.filter(approval_status=ApprovalStatus.PENDING.value).count()
    unapproved_chapters = Chapter.objects.filter(approved=False).count()
    total_requests = approved_novels + unapproved_chapters
    
    context = {
        'total_users': total_users,
        'total_novels': total_novels,
        'total_requests': total_requests,
        'approved_novels': approved_novels,
        'unapproved_chapters': unapproved_chapters,
    }
    return render(request, 'admin/home_admin.html', context)

@website_admin_required
def Dashboard(request):
    labels, data = getNewNovels()
    return render(request, 'admin/dashboard_admin.html', {
        'labels': labels,
        'data': data,
        'top_novels': top_novels_this_month,
        'new_novels': new_novels,
        'top_authors': authors,
    })
