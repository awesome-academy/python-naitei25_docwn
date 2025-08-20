from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from accounts.models import User
from .author import Author
from .artist import Artist
from .tag import Tag
from constants import (
    MAX_NAME_LENGTH,
    MAX_STATUS_LENGTH,
    MIN_RATE,
    MAX_RATE,
    COUNT_DEFAULT,
    ProgressStatus,
    ApprovalStatus,
)

class Novel(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    slug = models.SlugField(max_length=MAX_NAME_LENGTH, unique=True)
    summary = models.TextField()
    author = models.ForeignKey(
        Author, on_delete=models.SET_NULL, null=True, blank=True, related_name='novels'
    )
    artist = models.ForeignKey(
        Artist, on_delete=models.SET_NULL, null=True, blank=True, related_name='novels'
    )
    # Pending author/artist requests
    pending_author_request = models.ForeignKey(
        'AuthorRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='novels'
    )
    pending_artist_request = models.ForeignKey(
        'ArtistRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='novels'
    )
    tags = models.ManyToManyField(Tag, related_name='novels')
    image_url = models.TextField(null=True, blank=True)
    progress_status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=ProgressStatus.choices(),
        default=ProgressStatus.ONGOING.value,
        db_index=True,
    )
    approval_status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=ApprovalStatus.choices(),
        default=ApprovalStatus.DRAFT.value,
        db_index=True,
    )
    other_names = models.TextField(null=True, blank=True)
    word_count = models.IntegerField(default=COUNT_DEFAULT)
    view_count = models.IntegerField(default=COUNT_DEFAULT)
    favorite_count = models.IntegerField(default=COUNT_DEFAULT)
    rating_avg = models.FloatField(
        default=COUNT_DEFAULT,
        validators=[MinValueValidator(MIN_RATE), MaxValueValidator(MAX_RATE)]
    )
    
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_novels'
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text=_("Whether this novel should be displayed anonymously to public users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejected_reason = models.TextField(null=True, blank=True)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-view_count']),
            models.Index(fields=['-rating_avg']),
            models.Index(fields=['approval_status', '-created_at']),
            models.Index(fields=['progress_status']),
            models.Index(fields=['deleted_at'])
        ]
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from name
            if self.name and self.name.strip():
                base_slug = slugify(self.name.strip())
            else:
                base_slug = 'untitled-novel'
                
            if not base_slug:  # If slugify returns empty string (e.g., non-Latin characters)
                base_slug = 'novel'
            
            # Ensure uniqueness
            slug = base_slug
            counter = 1
            while Novel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
            
        # Ensure required fields have values
        if not self.name or not self.name.strip():
            self.name = "Untitled Novel"
            
        if not self.summary or not self.summary.strip():
            self.summary = "No summary available"
        
        super().save(*args, **kwargs)
