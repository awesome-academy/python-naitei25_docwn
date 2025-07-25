from django.db import models

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
    pass


class Artist(PersonBase):
    pass


class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_LENGTH, unique=True)


class Novel(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    summary = models.TextField()
    author = models.ForeignKey(
        Author, on_delete=models.SET_NULL, null=True, blank=True
    )
    artist = models.ForeignKey(
        Artist, on_delete=models.SET_NULL, null=True, blank=True
    )
    image_url = models.TextField(null=True, blank=True)
    progess_status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=ProgressStatus.choices(),
        default=ProgressStatus.ONGOING.value,
    )
    approval_status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=ApprovalStatus.choices(),
        default=ApprovalStatus.DRAFT.value,
    )
    other_names = models.TextField(null=True, blank=True)
    word_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    rating_avg = models.FloatField(default=0)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejected_reason = models.TextField(null=True, blank=True)


class NovelTag(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("novel", "tag")


class Volume(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    position = models.IntegerField()


class Chapter(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE)
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    length = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    rejected_reason = models.TextField(null=True, blank=True)
    is_hidden = models.BooleanField(default=False)


class Chunk(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    position = models.IntegerField()
    content = models.TextField()


class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
