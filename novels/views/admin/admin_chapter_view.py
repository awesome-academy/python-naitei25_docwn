from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from novels.models import Chapter
from common.decorators import website_admin_required
from django.core.paginator import Paginator
from django.db.models import Q
from constants import (
    ApprovalStatus,
    DATE_FORMAT_DMYHI,
    PAGINATOR_COMMON_LIST,
    PAGINATION_PAGE_RANGE,
    DEFAULT_PAGE_NUMBER,
    DATE_FORMAT_DMY,
)

@website_admin_required
def request_chapter_admin(request):
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    chapters = Chapter.objects.filter(
        approved=False,
        is_hidden=False,
        rejected_reason__isnull=True
    ).select_related(
        'volume__novel',  
        'volume__novel__created_by'  
    ).order_by('-created_at')
    
    # Add search functionality
    if search_query:
        chapters = chapters.filter(
            Q(title__icontains=search_query) |
            Q(volume__novel__name__icontains=search_query) |
            Q(volume__novel__created_by__username__icontains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(chapters, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page)

    return render(request, 'admin/request_chapter_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })

@require_POST
@website_admin_required
def approve_chapter_view(request, chapter_slug):
    try:
        # Try to get a single chapter first
        chapter = Chapter.objects.get(slug=chapter_slug)
    except Chapter.DoesNotExist:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('novels:request_chapter_admin')
    except Chapter.MultipleObjectsReturned:
        # If multiple chapters have the same slug, get the most recent unapproved one
        chapter = Chapter.objects.filter(
            slug=chapter_slug,
            approved=False
        ).order_by('-created_at').first()
        
        if not chapter:
            messages.error(request, _('Không tìm thấy chương chưa được duyệt với slug này.'))
            return redirect('novels:request_chapter_admin')
    
    chapter.approved = True
    chapter.rejected_reason = None
    chapter.save()

    messages.success(request, _('Chương "%(title)s" đã được duyệt thành công!') % {'title': chapter.title})
    return redirect('novels:chapter_review', chapter_slug=chapter.slug)

@require_POST
@website_admin_required
def reject_chapter_view(request, chapter_slug):
    try:
        # Try to get a single chapter first
        chapter = Chapter.objects.get(slug=chapter_slug)
    except Chapter.DoesNotExist:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('novels:request_chapter_admin')
    except Chapter.MultipleObjectsReturned:
        # If multiple chapters have the same slug, get the most recent unapproved one
        chapter = Chapter.objects.filter(
            slug=chapter_slug,
            approved=False
        ).order_by('-created_at').first()
        
        if not chapter:
            messages.error(request, _('Không tìm thấy chương chưa được duyệt với slug này.'))
            return redirect('novels:request_chapter_admin')
    
    rejected_reason = request.POST.get('rejected_reason', '').strip()

    if not rejected_reason:
        messages.error(request, _('Vui lòng cung cấp lý do từ chối.'))
        return redirect('novels:chapter_review', chapter_slug=chapter.slug)

    chapter.approved = False
    chapter.rejected_reason = rejected_reason
    chapter.save()

    messages.success(request, _('Chương "%(title)s" đã bị từ chối.') % {'title': chapter.title})
    return redirect('novels:chapter_review', chapter_slug=chapter.slug)

@website_admin_required
def chapter_review(request, chapter_slug):
    try:
        # Try to get a single chapter first
        chapter = Chapter.objects.get(slug=chapter_slug)
    except Chapter.DoesNotExist:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('novels:request_chapter_admin')
    except Chapter.MultipleObjectsReturned:
        # If multiple chapters have the same slug, get the most recent unapproved one
        chapter = Chapter.objects.filter(
            slug=chapter_slug,
            approved=False,
            is_hidden=False
        ).order_by('-created_at').first()
        
        if not chapter:
            # If no unapproved chapters, get the most recent one
            chapter = Chapter.objects.filter(slug=chapter_slug).order_by('-created_at').first()
        
        if not chapter:
            messages.error(request, _('Chương không tồn tại.'))
            return redirect('novels:request_chapter_admin')
    
    context = {
        'chapter': chapter,
        'novel': chapter.novel,
        'volume': chapter.volume,
        'content': chapter.get_content(),
        'next_chapter': chapter.get_next_chapter(),
        'previous_chapter': chapter.get_previous_chapter(),
        'chunks': chapter.chunks.all().order_by('position'),
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
    }

    return render(request, 'admin/chapter_review.html', context)
