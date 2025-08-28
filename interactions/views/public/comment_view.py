from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from common.utils.sse import send_notification_to_user
from interactions.models import Comment
from interactions.forms.comment_form import CommentForm

from interactions.models.notification import Notification
from novels.models import Novel
from interactions.services.comment_service import CommentService
from django.http import JsonResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
from constants import DEFAULT_PAGE_NUMBER
from django.urls import reverse
from interactions.forms.report_form import ReportForm
from django.core.paginator import Paginator
import logging
from django.contrib.contenttypes.models import ContentType
from asgiref.sync import async_to_sync

def novel_comments(request, novel_slug):
    """API trả về HTML comment phân trang"""
    page = request.GET.get("page", DEFAULT_PAGE_NUMBER)
    novel = get_object_or_404(Novel, slug=novel_slug)

    comments_page = CommentService.get_novel_comments(novel, page=page)
    report_form = ReportForm()
    html = render_to_string("novels/includes/comment_list.html", {
        "comments": comments_page,
        "novel_slug": novel_slug,
        "report_form": report_form,
    }, request=request)

    return JsonResponse({
        "html": html,
        "has_next": comments_page.has_next(),
        "has_prev": comments_page.has_previous(),
        "page": comments_page.number,
        "num_pages": comments_page.paginator.num_pages,
    })

@login_required
def add_comment(request, novel_slug):
    novel = get_object_or_404(Novel, slug=novel_slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        parent_id = request.POST.get('parent_comment_id')
        parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None
        
        if form.is_valid():
            comment = Comment.objects.create(
                novel=novel,
                user=request.user,
                content=form.cleaned_data['content'],
                parent_comment=parent_comment
            )

            comments_page = CommentService.get_novel_comments(novel, page=DEFAULT_PAGE_NUMBER)
            report_form = ReportForm()
            html = render_to_string("novels/includes/comment_list.html", {
                "comments": comments_page,
                "report_form": report_form,
                "novel_slug": novel_slug
            }, request=request)
            if not parent_comment:
                html = render_to_string(
                    "interactions/includes/comment.html",
                    {
                        "comment": comment,
                        "user": request.user,
                        "novel_slug": novel.slug
                    }
                )
            else:  # Nếu là reply, render reply.html
                html = render_to_string(
                    "interactions/includes/reply.html",
                    {
                        "comment": comment,  # đây là reply
                        "user": request.user
                    }
                )
                notify_user_reply_comment(comment)

            return JsonResponse({
                "success": True,
                "html": html,
                "has_next": comments_page.has_next(),
                "has_prev": comments_page.has_previous(),
                "page": comments_page.number,
                "num_pages": comments_page.paginator.num_pages,
                "content": comment.content,
                "parent_id": comment.parent_comment.id if comment.parent_comment else None,
            })
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return HttpResponseNotAllowed(['POST'])

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.is_active = False
    comment.save()
    return JsonResponse({"success": True, "id": comment_id})

logger = logging.getLogger(__name__)

def notify_user_reply_comment(reply_comment):
    parent_comment = reply_comment.parent_comment
    if not parent_comment or parent_comment.user == reply_comment.user:
        return

    parent_user = parent_comment.user
    novel = reply_comment.novel

    notification = Notification.objects.create(
        user=parent_user,
        type="REPLY_COMMENT",
        title="Bình luận của bạn được trả lời",
        content=f"{reply_comment.user.username} đã trả lời bình luận của bạn: '{reply_comment.content[:50]}…'",
        content_type=ContentType.objects.get_for_model(reply_comment),
        object_id=reply_comment.id,
    )

    redirect_url = reverse("novels:novel_detail", kwargs={"novel_slug": novel.slug})
    redirect_url += f"#comment-{parent_comment.id}"


    try:
        async_to_sync(send_notification_to_user)(
            user_id=parent_user.id,
            notification=notification,
            redirect_url=redirect_url,
        )
    except Exception as e:
        logger.exception("Lỗi khi gửi SSE cho user %s: %s", parent_user.id, e)

