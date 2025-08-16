from novels.models import ReadingHistory
from constants import PROGRESS_DEFAULT

class ReadingService:
    @staticmethod
    def get_or_create_reading_history(user, chapter):
        """Get or create reading history for user and chapter"""
        if not user.is_authenticated:
            return None
        
        reading_history, created = ReadingHistory.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={
                'novel': chapter.volume.novel,
                'reading_progress': PROGRESS_DEFAULT
            }
        )
        return reading_history
    
    @staticmethod
    def save_reading_progress(user, chapter_id, chunk_position, reading_progress):
        """Save user's reading progress"""
        from django.shortcuts import get_object_or_404
        from novels.models import Chapter
        
        chapter = get_object_or_404(Chapter, id=chapter_id)
        
        reading_history, created = ReadingHistory.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={'novel': chapter.volume.novel}
        )
        
        reading_history.reading_progress = reading_progress
        reading_history.current_chunk_position = chunk_position
        reading_history.save()
        
        return reading_history
