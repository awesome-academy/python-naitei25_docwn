from .helpers import count_words
from .simple_chunker import SimpleChunker

class ChunkManager:
    """Manager class for handling chapter content chunking operations."""
    
    @staticmethod
    def create_normal_chunks_for_chapter(chapter, content: str, chunker: SimpleChunker = None):
        """
        Create chunks for a chapter using simple normal chunking.
        
        Args:
            chapter: Chapter model instance
            content: Raw content to be chunked
            chunker: Optional SimpleChunker instance
        """
        from novels.models import Chunk
        
        if chunker is None:
            chunker = SimpleChunker()
            
        # Calculate total word count from original content first
        total_word_count = count_words(content)
        
        # Clear existing chunks
        Chunk.objects.filter(chapter=chapter).delete()
        
        # Create new chunks
        chunks_data = chunker.split_into_chunks(content)
        
        for position, (chunk_content, word_count) in enumerate(chunks_data, 1):
            Chunk.objects.create(
                chapter=chapter,
                position=position,
                content=chunk_content,
                word_count=word_count
            )
        
        # Update chapter word count with pre-calculated total
        chapter.word_count = total_word_count
        chapter.save(update_fields=['word_count'])
        
        return len(chunks_data)
    
    @staticmethod
    def create_chunks_for_chapter(chapter, content: str, chunker: SimpleChunker = None):
        """
        Create chunks for a chapter using normal chunking.
        
        Args:
            chapter: Chapter model instance
            content: Raw content to be chunked  
            chunker: Optional SimpleChunker instance
        """
        return ChunkManager.create_normal_chunks_for_chapter(chapter, content, chunker)
    
    @staticmethod
    def update_chapter_chunks(chapter, new_content: str, chunker: SimpleChunker = None):
        """
        Update chunks for an existing chapter.
        
        Args:
            chapter: Chapter model instance
            new_content: New content to replace existing chunks
            chunker: Optional SimpleChunker instance
        """
        return ChunkManager.create_normal_chunks_for_chapter(chapter, new_content, chunker)
