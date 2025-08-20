from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Q
from novels.models import Chapter
from constants import (
    PAGINATOR_COMMON_LIST,
    DEFAULT_PAGE_NUMBER,
    ApprovalStatus
)

class ChapterService:
    @staticmethod
    def get_chapter_for_user(chapter_slug, novel_slug, user=None):
        """Get chapter based on user permissions"""
        try:
            # First try public access
            chapter = Chapter.objects.select_related('volume__novel').get(
                slug=chapter_slug,
                volume__novel__slug=novel_slug,
                is_hidden=False,
                approved=True,
                deleted_at__isnull=True
            )
            return chapter
        except Chapter.DoesNotExist:
            # If not found and user is authenticated, check ownership
            if user and user.is_authenticated:
                return get_object_or_404(
                    Chapter.objects.select_related('volume__novel'),
                    slug=chapter_slug,
                    volume__novel__slug=novel_slug,
                    volume__novel__created_by=user,
                    deleted_at__isnull=True
                )
            else:
                raise Http404("No Chapter matches the given query.")
    
    @staticmethod
    def get_chapter_navigation(chapter):
        """Get next and previous chapters"""
        return {
            'next_chapter': chapter.get_next_chapter(),
            'prev_chapter': chapter.get_previous_chapter()
        }
    
    @staticmethod
    def get_all_chapters_for_novel(novel, user=None):
        """Get all chapters for a novel based on user permissions"""
        if user and user.is_authenticated and novel.created_by == user:
            # Owner can see all non-deleted chapters
            return Chapter.objects.filter(
                volume__novel=novel,
                deleted_at__isnull=True
            ).select_related('volume').order_by('volume__position', 'position')
        else:
            # Public view - only approved and visible chapters
            return Chapter.objects.filter(
                volume__novel=novel,
                approved=True,
                is_hidden=False,
                deleted_at__isnull=True
            ).select_related('volume').order_by('volume__position', 'position')
    
    @staticmethod
    def get_chapter_chunks_stats(chapter):
        """Calculate chapter chunking statistics"""
        from constants import WORDS_PER_MINUTE
        
        all_chunks = chapter.chunks.all()
        total_chunks = all_chunks.count()
        
        chunk_word_counts = [chunk.word_count for chunk in all_chunks]
        avg_chunk_size = sum(chunk_word_counts) / len(chunk_word_counts) if chunk_word_counts else 0
        max_chunk_words = max(chunk_word_counts) if chunk_word_counts else 0
        estimated_reading_time = chapter.word_count / WORDS_PER_MINUTE
        
        return {
            'all_chunks': all_chunks,
            'total_chunks': total_chunks,
            'avg_chunk_size': avg_chunk_size,
            'max_chunk_words': max_chunk_words,
            'estimated_reading_time': estimated_reading_time
        }

    @staticmethod
    def get_pending_chapters_for_admin(search_query='', page=DEFAULT_PAGE_NUMBER):
        """Get paginated list of chapters pending approval"""
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
        
        return page_obj

    @staticmethod
    def get_chapter_by_slug(chapter_slug, for_review=False):
        try:
            chapter = Chapter.objects.select_related(
                'volume__novel',
                'volume__novel__created_by'
            ).get(slug=chapter_slug)
            return chapter
        except Chapter.DoesNotExist:
            return None
        except Chapter.MultipleObjectsReturned:
            if for_review:
                chapter = Chapter.objects.filter(
                    slug=chapter_slug,
                    approved=False,
                    rejected_reason__isnull=True,
                    is_hidden=False
                ).select_related(
                    'volume__novel',
                    'volume__novel__created_by'
                ).order_by('-created_at').first()
                
                if not chapter:
                    chapter = Chapter.objects.filter(
                        slug=chapter_slug
                    ).select_related(
                        'volume__novel',
                        'volume__novel__created_by'
                    ).order_by('-created_at').first()
                
                return chapter
            else:
                chapter = Chapter.objects.filter(
                    slug=chapter_slug,
                    approved=False
                ).select_related(
                    'volume__novel',
                    'volume__novel__created_by'
                ).order_by('-created_at').first()
                
                return chapter

    @staticmethod
    def approve_chapter(chapter):
        """Approve a chapter"""
        chapter.approved = True
        chapter.rejected_reason = None
        chapter.save()
        return chapter

    @staticmethod
    def reject_chapter(chapter, rejected_reason):
        """Reject a chapter with reason"""
        chapter.approved = False
        chapter.rejected_reason = rejected_reason
        chapter.save()
        return chapter

    @staticmethod
    def get_chapter_review_context(chapter):
        """Get complete context for chapter review"""
        chunks = chapter.chunks.all().order_by('position')
        navigation = ChapterService.get_chapter_navigation(chapter)
        
        return {
            'chapter': chapter,
            'novel': chapter.volume.novel,
            'volume': chapter.volume,
            'content': chapter.get_content(),
            'next_chapter': navigation['next_chapter'],
            'previous_chapter': navigation['prev_chapter'],
            'chunks': chunks,
        }
        
    @staticmethod
    def get_earliest_unapproved_chapter(novel):
        return Chapter.objects.filter(
            volume__novel=novel,
            approved=False,
            rejected_reason__isnull=True,
            is_hidden=False,
            deleted_at__isnull=True
        ).order_by('created_at').first()

    @staticmethod
    def create_chapter(form, novel):
        """Create a new chapter from form"""
        chapter = form.save()
        return chapter

    @staticmethod
    def can_user_add_chapter(novel, user):
        """Check if user can add chapter to novel"""
        return (novel.created_by == user and
                novel.approval_status == ApprovalStatus.APPROVED.value)

    @staticmethod
    def get_user_chapter_for_deletion(chapter_slug, novel_slug, user):
        """Get chapter for deletion with ownership check"""
        chapter = get_object_or_404(
            Chapter.objects.select_related('volume__novel'),
            slug=chapter_slug,
            volume__novel__slug=novel_slug,
            deleted_at__isnull=True
        )
        
        if chapter.volume.novel.created_by != user:
            return None
        
        return chapter

    @staticmethod
    def soft_delete_chapter(chapter):
        """Perform soft delete on chapter"""
        chapter.deleted_at = timezone.now()
        chapter.save(update_fields=['deleted_at'])
        return chapter
