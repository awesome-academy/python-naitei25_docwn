from django.db.models import OuterRef, Subquery, Q, Prefetch
from django.core.paginator import Paginator
from novels.models import Novel, Volume, Chapter, Tag, Favorite
from django.db import IntegrityError
from django.db import transaction
from constants import (
    ApprovalStatus, ProgressStatus, MAX_TREND_NOVELS, 
    MAX_LIKE_NOVELS, MAX_FINISH_NOVELS, MAX_NEWUPDATE_NOVELS,
    MAX_LATEST_CHAPTER, NOVEL_PER_PAGE, PAGINATOR_COMMON_LIST,
    SEARCH_RESULTS_LIMIT, SUMMARY_TRUNCATE_WORDS, DEFAULT_RATING_AVERAGE,
    MAX_CHAPTER_LIST,MAX_LIKE_NOVELS_PAGE, NotificationTypeChoices
)
from interactions.services.notification_service import NotificationService
from django.utils.translation import gettext_lazy as _
from common.utils.sse import SSEManager
from asgiref.sync import async_to_sync

class NovelService:
    @staticmethod
    def get_approved_novels():
        """Get all approved and non-deleted novels"""
        return Novel.objects.filter(
            approval_status=ApprovalStatus.APPROVED.value, 
            deleted_at__isnull=True
        )
    
    @staticmethod
    def get_trend_novels():
        """Get trending novels based on view count"""
        return NovelService.get_approved_novels().order_by('-view_count')[:MAX_TREND_NOVELS]
    @staticmethod
    def get_more_trend_novels():
        """Get trending novels based on view count"""
        return NovelService.get_approved_novels().order_by('-view_count')
    
    @staticmethod
    def get_new_novels():
        """Get newest novels"""
        return NovelService.get_approved_novels().order_by('-created_at')
    
    @staticmethod
    def get_like_novels():
        """Get most liked novels"""
        return NovelService.get_approved_novels().order_by('-favorite_count')[:MAX_LIKE_NOVELS]
    
    @staticmethod
    def get_finished_novels_with_chapters():
        """Get finished novels with their latest volumes and chapters"""
        finish_novels = Novel.objects.filter(
            progress_status=ProgressStatus.COMPLETED.value,
            approval_status=ApprovalStatus.APPROVED.value,
            volumes__chapters__isnull=False 
        ).order_by('-updated_at')
        
        novel_ids = list(finish_novels.values_list('id', flat=True)[:MAX_FINISH_NOVELS])
        
        all_volumes = Volume.objects.filter(novel_id__in=novel_ids).order_by('-updated_at')
        all_chapters = Chapter.objects.filter(volume__novel_id__in=novel_ids).order_by('-updated_at')
        
        # Build dictionaries for efficient lookup
        recent_volume_dict = {}
        for volume in all_volumes:
            if volume.novel_id not in recent_volume_dict:
                recent_volume_dict[volume.novel_id] = volume
        
        recent_chapter_dict = {}
        for chapter in all_chapters:
            vol_id = chapter.volume_id
            if vol_id in [v.id for v in recent_volume_dict.values()]:
                if vol_id not in recent_chapter_dict:
                    recent_chapter_dict[vol_id] = chapter
        
        # Attach recent volumes and chapters to novels
        for novel in finish_novels:
            recent_volume = recent_volume_dict.get(novel.id)
            novel.recent_volume = recent_volume
            if recent_volume:
                recent_chapter = Chapter.objects.filter(
                    volume=recent_volume
                ).order_by('-updated_at').first()
                novel.recent_chapter = recent_chapter
        
        return finish_novels
    
    @staticmethod
    def get_recent_volumes_for_cards(limit=MAX_LATEST_CHAPTER):
        """Get recent volumes with their latest chapters for homepage cards"""
        
        # Get the most recent chapter for each volume
        latest_chapter_subquery = Chapter.objects.filter(
            volume_id=OuterRef('pk'),
            approved=True,
            is_hidden=False,
            deleted_at__isnull=True
        ).order_by('-updated_at').values('title', 'updated_at')[:1]

        # Get volumes with approved novels, ordered by their latest chapter update
        volumes = Volume.objects.select_related('novel').filter(
            novel__approval_status=ApprovalStatus.APPROVED.value,
            novel__deleted_at__isnull=True,
            chapters__approved=True,
            chapters__is_hidden=False,
            chapters__deleted_at__isnull=True
        ).annotate(
            recent_chapter_title=Subquery(latest_chapter_subquery.values('title')),
            latest_chapter_update=Subquery(latest_chapter_subquery.values('updated_at'))
        ).filter(
            recent_chapter_title__isnull=False
        ).distinct().order_by('-latest_chapter_update')[:limit]
        
        return [{
            'name': vol.novel.name,  
            'slug': vol.novel.slug,  
            'image_url': vol.novel.image_url,
            'recent_volume': {
                'name': vol.name
            },
            'recent_chapter': {
                'title': vol.recent_chapter_title
            } if vol.recent_chapter_title else None
        } for vol in volumes]

    @staticmethod
    def get_user_novels_with_stats(user):
        """Get user novels with status statistics"""
        user_novels = Novel.objects.filter(
            created_by=user,
            deleted_at__isnull=True
        )
        
        return {
            'novels': user_novels,
            'total_count': user_novels.count(),
            'draft_count': user_novels.filter(approval_status=ApprovalStatus.DRAFT.value).count(),
            'pending_count': user_novels.filter(approval_status=ApprovalStatus.PENDING.value).count(),
            'approved_count': user_novels.filter(approval_status=ApprovalStatus.APPROVED.value).count(),
            'rejected_count': user_novels.filter(approval_status=ApprovalStatus.REJECTED.value).count(),
        }

    @staticmethod
    def get_novel_detail(novel_slug, user=None):
        """Get novel detail with tags and volumes"""
        try:
            novel = Novel.objects.select_related('author', 'artist', 'created_by').prefetch_related('tags').get(slug=novel_slug)
        except Novel.DoesNotExist:
            return None
            
        # Check permissions
        if user != novel.created_by:
            if novel.approval_status != ApprovalStatus.APPROVED.value:
                return None
        
        tags = list(novel.tags.all())
        volumes = Volume.objects.filter(novel=novel).prefetch_related("chapters").order_by('position', 'created_at')
        is_owner = user and user.is_authenticated and novel.created_by == user
        
        # Process volumes and chapters
        for volume in volumes:
            if is_owner:
                volume.chapter_list = list(volume.chapters.filter(deleted_at__isnull=True).order_by('position', 'created_at'))
            else:
                volume.chapter_list = list(volume.chapters.filter(
                    approved=True, is_hidden=False, deleted_at__isnull=True
                ).order_by('position', 'created_at'))
            
            volume.remaining_chapters = max(len(volume.chapter_list) - MAX_CHAPTER_LIST, 0)

        can_add_chapter = (
            user and user.is_authenticated and
            novel.created_by == user and
            novel.approval_status == ApprovalStatus.APPROVED.value
        )

        return {
            'novel': novel,
            'tags': tags,
            'volumes': volumes,
            'is_owner': is_owner,
            'can_add_chapter': can_add_chapter
        }

    @staticmethod
    def get_user_novels_paginated(user, status_filter=None, page=1):
        """Get paginated user novels with filtering"""
        queryset = Novel.objects.filter(
            created_by=user,
            deleted_at__isnull=True
        ).select_related('author', 'artist').prefetch_related('tags')
        
        # Apply status filter
        valid_statuses = [choice[0] for choice in ApprovalStatus.choices()]
        if status_filter and status_filter in valid_statuses:
            queryset = queryset.filter(approval_status=status_filter)
        
        queryset = queryset.order_by('-created_at')
        
        # Paginate
        paginator = Paginator(queryset, NOVEL_PER_PAGE)
        page_obj = paginator.get_page(page)
        
        # Process novels data
        for novel in page_obj:
            novel.tag_list = list(novel.tags.all())
            novel.author_name = novel.author.name if novel.author and not novel.is_anonymous else None
            novel.rating_display = novel.rating_avg if hasattr(novel, 'rating_avg') and novel.rating_avg > 0 else None
            novel.can_edit = novel.approval_status in [ApprovalStatus.DRAFT.value, ApprovalStatus.REJECTED.value]
            novel.can_manage_chapters = novel.approval_status == ApprovalStatus.APPROVED.value
            novel.is_rejected_with_reason = (
                novel.approval_status == ApprovalStatus.REJECTED.value and 
                hasattr(novel, 'rejected_reason') and novel.rejected_reason
            )
        
        return page_obj

    @staticmethod
    def search_novels(query):
        """Search novels by multiple fields"""
        if not query:
            return Novel.objects.none()
            
        novels = Novel.objects.filter(
            Q(name__icontains=query) |
            Q(summary__icontains=query) |
            Q(author__name__icontains=query) |
            Q(artist__name__icontains=query) |
            Q(other_names__icontains=query) |
            Q(tags__name__icontains=query),
            approval_status=ApprovalStatus.APPROVED.value,
            deleted_at__isnull=True
        ).select_related('author', 'artist').prefetch_related('tags').distinct().order_by('-view_count')
        
        # Process data for template
        for novel in novels:
            novel.tag_list = list(novel.tags.all())
            novel.rating_display = getattr(novel, 'rating_avg', DEFAULT_RATING_AVERAGE) if hasattr(novel, 'rating_avg') and novel.rating_avg > 0 else DEFAULT_RATING_AVERAGE
            
        return novels

    @staticmethod
    def get_admin_novels_paginated(search_query=None, progress_status=None, tag_id=None, approval_status=None, page=1):
        if not approval_status:  
            novels = Novel.objects.filter(deleted_at__isnull=True)
        else:
            novels = Novel.objects.filter(
            approval_status=approval_status,
            deleted_at__isnull=True
             )
        novels = novels.select_related('author').prefetch_related('tags').order_by('-created_at')

    # Search filter
        if search_query:
            novels = novels.filter(
            Q(name__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()

    # Filter progress_status nếu có
        if progress_status:
            novels = novels.filter(progress_status=progress_status)

    # Filter theo tag nếu có
        if tag_id:
            try:
                tag = Tag.objects.get(id=tag_id)   
                novels = novels.filter(tags=tag)
            except Tag.DoesNotExist:
                novels = novels.none()

    # Pagination
        paginator = Paginator(novels, PAGINATOR_COMMON_LIST)
        return paginator.get_page(page)

 

    @staticmethod
    def get_pending_novels_paginated(search_query=None, progress_status=None, tag_id=None, approval_status=None, page=1):
        if not approval_status:  
            novels = Novel.objects.filter(
            approval_status=ApprovalStatus.PENDING.value,
            deleted_at__isnull=True)
        else:
        
            novels = Novel.objects.filter(
            approval_status=approval_status,
            deleted_at__isnull=True
        )

    # Thêm select_related, prefetch_related và order
        novels = novels.select_related('author').prefetch_related('tags').order_by('-created_at')

    # Search filter
        if search_query:
            novels = novels.filter(
            Q(name__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()

    # Filter progress_status nếu có
        if progress_status:
            novels = novels.filter(progress_status=progress_status)

    # Filter theo tag nếu có
        if tag_id:
            try:
                tag = Tag.objects.get(id=tag_id)   
                novels = novels.filter(tags=tag)
            except Tag.DoesNotExist:
                novels = novels.none()

    # Pagination
        paginator = Paginator(novels, PAGINATOR_COMMON_LIST)
        return paginator.get_page(page)


    @staticmethod
    def get_admin_novel_detail(slug):
        """Get novel detail for admin"""
        try:
            novel = Novel.objects.select_related('author', 'artist', 'created_by').prefetch_related('tags').get(slug=slug)
            tags = list(novel.tags.all())
            return {
                'novel': novel,
                'tags': tags
            }
        except Novel.DoesNotExist:
            return None

    @staticmethod
    def get_pending_novel_detail(slug):
        """Get pending novel detail for admin"""
        try:
            novel = Novel.objects.select_related('author', 'artist', 'created_by').prefetch_related('tags').get(
                slug=slug, 
                approval_status=ApprovalStatus.PENDING.value
            )
            tags = list(novel.tags.all())
            return {
                'novel': novel,
                'tags': tags
            }
        except Novel.DoesNotExist:
            return None

    @staticmethod
    def approve_novel(slug):
        """Approve a pending novel"""
        try:
            novel = Novel.objects.get(slug=slug, approval_status=ApprovalStatus.PENDING.value)
            
            # Check if author is approved before approving novel
            if novel.author:
                # If novel has a direct author reference, check if author exists (means it's approved)
                pass  # Author is already approved since it exists in Author table
            elif novel.pending_author_request:
                # If novel has pending author request, check if it's approved
                if novel.pending_author_request.approval_status != ApprovalStatus.APPROVED.value:
                    return {'success': False, 'reason': 'author_not_approved'}
            else:
                # Novel has no author - this might be allowed depending on business rules
                # For now, we'll allow novels without authors to be approved
                pass
            
            novel.approval_status = ApprovalStatus.APPROVED.value
            novel.save()
            return {'success': True, 'novel': novel}
        except Novel.DoesNotExist:
            return {'success': False, 'reason': 'novel_not_found'}

    @staticmethod
    def reject_novel(slug, reason=None):
        """Reject a pending novel with reason"""
        try:
            novel = Novel.objects.get(slug=slug, approval_status=ApprovalStatus.PENDING.value)
            novel.approval_status = ApprovalStatus.REJECTED.value
            if reason:
                novel.rejected_reason = reason
            novel.save()

            return novel
        except Novel.DoesNotExist:
            return False

class FavoriteService:
    @staticmethod
    @transaction.atomic
    def toggle_like(user, novel):
        fav = Favorite.objects.filter(user=user, novel=novel).first()
        if fav:
            fav.delete()
            return False
        else:
            Favorite.objects.create(user=user, novel=novel)
            return True

def get_liked_novels(user, page_number, per_page=MAX_LIKE_NOVELS_PAGE):
    favorites = Favorite.objects.filter(user=user).select_related("novel")
    novels = [f.novel for f in favorites]

    paginator = Paginator(novels, per_page)
    return paginator.get_page(page_number)
