from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from constants import (
    MAX_NAME_LENGTH,
    MAX_COUNTRY_LENGTH,
    MAX_TAG_LENGTH,
    MAX_TITLE_LENGTH,
    MAX_GENDER_LENGTH,
    MAX_STATUS_LENGTH,
    Gender,
    ProgressStatus,
    ApprovalStatus,
    MIN_RATE,
    MAX_RATE,
    COUNT_DEFAULT,
    PROGRESS_DEFAULT
)


class PersonBase(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    pen_name = models.CharField(
        max_length=MAX_NAME_LENGTH, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    deathday = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=MAX_GENDER_LENGTH,
        choices=Gender.choices(),
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=MAX_COUNTRY_LENGTH, null=True, blank=True
    )
    image_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Author(PersonBase):
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

class Artist(PersonBase):
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_LENGTH, unique=True)
    slug = models.SlugField(max_length=MAX_TAG_LENGTH, unique=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name


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
    tags = models.ManyToManyField(Tag, through='NovelTag', related_name='novels')
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


class NovelTag(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.RESTRICT)
    tag = models.ForeignKey(Tag, on_delete=models.RESTRICT)

    class Meta:
        unique_together = ("novel", "tag")
        indexes = [
            models.Index(fields=['novel', 'tag']),
        ]


class Volume(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.RESTRICT, related_name='volumes')
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('novel', 'position')
        ordering = ['position']
        indexes = [
            models.Index(fields=['novel', 'position']),
        ]
        
    def __str__(self):
        return f"{self.novel.name} - {self.name}"


class Chapter(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.RESTRICT, related_name='chapters')
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    slug = models.SlugField(max_length=MAX_TITLE_LENGTH)
    position = models.IntegerField()
    word_count = models.IntegerField(default=COUNT_DEFAULT)
    view_count = models.IntegerField(default=COUNT_DEFAULT)
    approved = models.BooleanField(default=False, db_index=True)
    rejected_reason = models.TextField(null=True, blank=True)
    is_hidden = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('volume', 'position')
        ordering = ['volume', 'position']
        indexes = [
            models.Index(fields=['volume', 'position']),
            models.Index(fields=['approved', 'is_hidden']),
        ]
        
    def __str__(self):
        return f"{self.volume.novel.name} - {self.title}"
    
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
            is_hidden=False
        ).order_by('volume__position', 'position').first()
    
    def get_previous_chapter(self):
        return Chapter.objects.filter(
            volume__novel=self.volume.novel,
            volume__position__lte=self.volume.position,
            position__lt=self.position,
            approved=True,
            is_hidden=False
        ).order_by('-volume__position', '-position').first()


class Chunk(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.RESTRICT, related_name='chunks')
    position = models.IntegerField()
    content = models.TextField()
    word_count = models.IntegerField(default=COUNT_DEFAULT)
    
    class Meta:
        unique_together = ('chapter', 'position')
        ordering = ['position']
        indexes = [
            models.Index(fields=['chapter', 'position']),
        ]
        
    def __str__(self):
        return f"{self.chapter.title} - Chunk {self.position}"


class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='reading_history')
    chapter = models.ForeignKey(Chapter, on_delete=models.RESTRICT, related_name='reading_history')
    novel = models.ForeignKey(Novel, on_delete=models.RESTRICT, related_name='reading_history')
    read_at = models.DateTimeField(auto_now_add=True)
    reading_progress = models.FloatField(default=PROGRESS_DEFAULT)

    class Meta:
        unique_together = ('user', 'chapter')
        indexes = [
            models.Index(fields=['user', '-read_at']),
            models.Index(fields=['user', 'novel', '-read_at']),
            models.Index(fields=['chapter']),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='favorites')
    novel = models.ForeignKey(Novel, on_delete=models.RESTRICT, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'novel')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['novel']),
        ]
