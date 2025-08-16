import re
from typing import List, Tuple
from constants import MAX_CHUNK_SIZE
from .helpers import count_words

class SimpleChunker:
    """
    A simple utility class for chunking text content based on database text field limits.
    Uses straightforward character-based chunking without complex semantic analysis.
    """
    
    def __init__(self, max_chunk_size: int = MAX_CHUNK_SIZE):
        """
        Initialize the simple chunker.
        
        Args:
            max_chunk_size: Maximum size of each chunk in characters (default: MAX_CHUNK_SIZE for MySQL TEXT)
        """
        self.max_chunk_size = max_chunk_size
        
    def split_into_chunks(self, content: str) -> List[Tuple[str, int]]:
        """
        Split content into simple chunks based on character limits.
        
        Args:
            content: The text content to chunk
            
        Returns:
            List of tuples containing (chunk_content, word_count)
        """
        if not content or not content.strip():
            return []
            
        # Clean and normalize content
        content = self._normalize_content(content)
        
        # Split into chunks
        chunks = self._create_simple_chunks(content)
        
        # Calculate word counts for each chunk
        result = []
        for chunk in chunks:
            word_count = count_words(chunk)
            # Only strip excessive leading/trailing whitespace, preserve paragraph structure
            chunk_clean = chunk.strip(' \t')  # Only strip spaces and tabs, keep newlines
            result.append((chunk_clean, word_count))
            
        return result
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for plain text."""
        # For plain text content, normalize whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Multiple blank lines to double
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single space
        return content.strip(' \t')  # Only strip spaces and tabs, preserve newlines
    
    def _create_simple_chunks(self, content: str) -> List[str]:
        """Create chunks by splitting at safe text boundaries."""
        chunks = []
        
        # If content is smaller than max size, return as single chunk
        if len(content) <= self.max_chunk_size:
            return [content]
        
        # Split content into chunks at safe text boundaries
        start = 0
        while start < len(content):
            end = start + self.max_chunk_size
            
            # If this is not the last chunk, find a safe breaking point
            if end < len(content):
                # Look for paragraph breaks (double newlines)
                paragraph_break = content.rfind('\n\n', start, end)
                if paragraph_break > start:
                    end = paragraph_break + 2
                else:
                    # Look for single line breaks
                    line_break = content.rfind('\n', start, end)
                    if line_break > start:
                        end = line_break + 1
                    else:
                        # Look for sentence endings
                        sentence_end = content.rfind('. ', start, end)
                        if sentence_end > start:
                            end = sentence_end + 2
                        else:
                            # Last resort: find whitespace
                            space = content.rfind(' ', start, end)
                            if space > start:
                                end = space + 1
                            # Otherwise, force break at max_chunk_size
            
            chunk = content[start:end].strip(' \t')  # Only strip spaces and tabs, preserve newlines
            if chunk:
                chunks.append(chunk)
            
            start = end
        
        return chunks

