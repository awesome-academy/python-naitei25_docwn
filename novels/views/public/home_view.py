from django.shortcuts import render
from novels.services import NovelService
from novels.utils import format_comments_for_template
from interactions.models import Comment
from constants import (
    ApprovalStatus,
    MAX_HOME_COMMENTS,
    MAX_MOST_READ_NOVELS,
    MAX_NEW_NOVELS
)
from ...fake_data import discussion_data, card_list

def Home(request):
    """Homepage view with all novel listings"""
    # Get novels using service
    trend_novels = NovelService.get_trend_novels()
    new_novels = NovelService.get_new_novels()
    like_novels = NovelService.get_like_novels()
    finish_novels = NovelService.get_finished_novels_with_chapters()
    newupdate_novels = NovelService.get_recent_volumes_for_cards()
    
    # Get recent comments
    comments = Comment.objects.select_related('user', 'novel', 'user__profile').filter(
        novel__approval_status=ApprovalStatus.APPROVED.value,
        novel__deleted_at__isnull=True,
        is_reported=False
    ).exclude(
        user__isnull=True
    ).order_by('-created_at')[:MAX_HOME_COMMENTS]
    
    comments_data = format_comments_for_template(comments)
    
    context = {
        "finish_novels": finish_novels,
        "trend_novels": trend_novels,
        "new_novels": new_novels,
        "discussion_data": discussion_data,
        "comments": comments_data,
        "newupdate_novels": newupdate_novels,
        "card_list": card_list,
        "like_novels": like_novels,
    }

    return render(request, 'novels/home.html', context)

def most_read_novels(request):
    """Most read novels page"""
    novels = NovelService.get_approved_novels().order_by('-view_count')[:MAX_MOST_READ_NOVELS]
    
    context = {'novels': novels}
    return render(request, 'novels/most_read_novels.html', context)

def new_novels(request):
    """New novels page"""  
    new_novels = NovelService.get_approved_novels().order_by('-created_at')[:MAX_NEW_NOVELS]
    
    context = {'new_novels': new_novels}
    return render(request, 'novels/new_novels.html', context)

def finish_novels(request):
    """Finished novels page"""
    finish_novels = NovelService.get_finished_novels_with_chapters()
    
    context = {'finish_novels': finish_novels}
    return render(request, 'novels/finish_novels.html', context)
