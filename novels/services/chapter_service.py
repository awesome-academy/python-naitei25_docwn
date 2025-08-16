from django.shortcuts import get_object_or_404
from django.http import Http404
from novels.models import Chapter

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
