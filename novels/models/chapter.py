from django.db import models
from django.db import IntegrityError
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from .volume import Volume
from constants import (
    MAX_TITLE_LENGTH,
    MAX_SLUG_LENGTH,
    MAX_RANDOM_STRING_LENGTH,
    COUNT_DEFAULT,
    MAX_ATTEMPTS
)

class Chapter(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.RESTRICT, related_name='chapters')
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    slug = models.SlugField(max_length=MAX_SLUG_LENGTH, unique=True)  # Uses constant for chapter slugs
    position = models.IntegerField()
    word_count = models.IntegerField(default=COUNT_DEFAULT)
    view_count = models.IntegerField(default=COUNT_DEFAULT)
    approved = models.BooleanField(default=False, db_index=True)
    rejected_reason = models.TextField(null=True, blank=True)
    is_hidden = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('volume', 'position')
        ordering = ['volume', 'position']
        indexes = [
            models.Index(fields=['volume', 'position']),
            models.Index(fields=['approved', 'is_hidden']),
            models.Index(fields=['deleted_at']),
        ]
        
    def __str__(self):
        return f"{self.volume.novel.name} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from volume name and chapter title
            volume_slug = slugify(self.volume.name) if self.volume.name else f'tap-{self.volume.position}'
            
            if self.title and self.title.strip():
                chapter_slug = slugify(self.title.strip())
            else:
                chapter_slug = f'chuong-{self.position}'
                
            # Combine volume and chapter information
            if chapter_slug:
                base_slug = f'{volume_slug}-{chapter_slug}'
            else:
                base_slug = f'{volume_slug}-chuong-{self.position}'
            
            # Ensure global uniqueness for admin URLs
            self.slug = base_slug
            for attempt in range(MAX_ATTEMPTS):
                try:
                    super().save(*args, **kwargs)
                    break
                except IntegrityError as e:
                    if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
                        rand = get_random_string(MAX_RANDOM_STRING_LENGTH)
                        self.slug = f"{self.slug}-{rand}"
                    else:
                        raise
    
    @property
    def novel(self):
        return self.volume.novel
    
    def get_content(self):
        chunks = self.chunks.all().order_by('position')
        return '\n'.join([chunk.content for chunk in chunks])
    
    def get_next_chapter(self):
        return Chapter.objects.filter(
            volume__novel=self.volume.novel,
            volume__position__gte=self.volume.position,
            position__gt=self.position,
            approved=True,
            is_hidden=False,
            deleted_at__isnull=True
        ).order_by('volume__position', 'position').first()
    
    def get_previous_chapter(self):
        return Chapter.objects.filter(
            volume__novel=self.volume.novel,
            volume__position__lte=self.volume.position,
            position__lt=self.position,
            approved=True,
            is_hidden=False,
            deleted_at__isnull=True
        ).order_by('-volume__position', '-position').first()
