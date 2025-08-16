from datetime import datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from constants import SECONDS_PER_HOUR, SECONDS_PER_MINUTE

def get_relative_time(created_at):
    """Get relative time string in Vietnamese"""
    if not created_at:
        return ''
    
    # Ensure we're working with timezone-aware datetime
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at)
    
    now = timezone.now()
    diff = now - created_at
    
    if diff.days > 0:
        return f"{diff.days} {_('ngày')}"
    elif diff.seconds >= SECONDS_PER_HOUR:
        hours = diff.seconds // SECONDS_PER_HOUR
        return f"{hours} {_('giờ')}"
    elif diff.seconds >= SECONDS_PER_MINUTE:
        minutes = diff.seconds // SECONDS_PER_MINUTE
        return f"{minutes} {_('phút')}"
    else:
        return _("Vừa xong")

def calculate_reading_time(word_count, words_per_minute=250):
    """Calculate estimated reading time in minutes"""
    if not word_count:
        return 0
    return word_count / words_per_minute

def format_comments_for_template(comments):
    """Format comments data for template compatibility"""
    from constants import COMMENT_TRUNCATE_LENGTH
    
    comments_data = []
    for comment in comments:
        avatar_url = None
        if comment.user and hasattr(comment.user, 'profile') and comment.user.profile:
            avatar_url = comment.user.profile.get_avatar()
        
        comments_data.append({
            'title': comment.novel.name if comment.novel else 'Unknown Novel',
            'comment': comment.content[:COMMENT_TRUNCATE_LENGTH] + '...' if len(comment.content) > COMMENT_TRUNCATE_LENGTH else comment.content,
            'username': comment.user.username if comment.user else 'Anonymous',
            'avatar': avatar_url,
            'time': get_relative_time(comment.created_at)
        })
    
    return comments_data

def count_words(text: str) -> int:
    """
    Count the number of words in a text string.
    
    Args:
        text: The text content to count words in
        
    Returns:
        int: Number of words in the text
    """
    if not text or not text.strip():
        return 0
    
    # Split by whitespace and filter out empty strings
    words = text.split()
    return len(words)
