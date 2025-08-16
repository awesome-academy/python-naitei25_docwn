from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Novel, Author, Artist, Tag, Chapter, Chunk, Volume
from .utils import ChunkManager

# Register your models here.


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "artist", "created_at", "updated_at")
    search_fields = ("name", "author__name", "artist__name")
    list_filter = ("author", "artist")
    ordering = ("-created_at",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "pen_name", "country", "created_at")
    search_fields = ("name", "pen_name")
    ordering = ("name",)
    list_filter = ("country",)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "pen_name", "country", "created_at")
    search_fields = ("name", "pen_name")
    ordering = ("name",)
    list_filter = ("country",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ("name", "novel", "position", "created_at")
    search_fields = ("name", "novel__name")
    list_filter = ("novel",)
    ordering = ("novel", "position")


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "volume", "position", "word_count", "chunk_count", "approved", "is_deleted", "created_at")
    search_fields = ("title", "volume__name", "volume__novel__name")
    list_filter = ("approved", "is_hidden", "volume__novel", "deleted_at")
    ordering = ("volume__novel", "volume__position", "position")
    actions = ["rechunk_chapters", "soft_delete_chapters", "restore_chapters"]
    
    def chunk_count(self, obj):
        return obj.chunks.count()
    chunk_count.short_description = "Chunks"
    
    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True
    is_deleted.short_description = "Deleted"
    
    def rechunk_chapters(self, request, queryset):
        """Action to re-chunk selected chapters using normal chunking."""
        updated_count = 0
        error_count = 0
        
        for chapter in queryset:
            try:
                content = chapter.get_content()
                if content.strip():
                    ChunkManager.create_normal_chunks_for_chapter(chapter, content)
                    updated_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                
        if updated_count > 0:
            messages.success(
                request, 
                f"Successfully re-chunked {updated_count} chapters using normal chunking."
            )
        if error_count > 0:
            messages.warning(
                request, 
                f"Failed to re-chunk {error_count} chapters (empty content or errors)."
            )
    
    rechunk_chapters.short_description = "Re-chunk selected chapters normally"
    
    def soft_delete_chapters(self, request, queryset):
        """Action to soft delete selected chapters."""
        from django.utils import timezone
        updated = queryset.filter(deleted_at__isnull=True).update(deleted_at=timezone.now())
        messages.success(request, f"Successfully soft deleted {updated} chapters.")
    soft_delete_chapters.short_description = "Soft delete selected chapters"
    
    def restore_chapters(self, request, queryset):
        """Action to restore soft deleted chapters."""
        updated = queryset.filter(deleted_at__isnull=False).update(deleted_at=None)
        messages.success(request, f"Successfully restored {updated} chapters.")
    restore_chapters.short_description = "Restore selected chapters"


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ("chapter", "position", "word_count", "content_preview")
    search_fields = ("chapter__title", "chapter__volume__name", "content")
    list_filter = ("chapter__volume__novel",)
    ordering = ("chapter__volume__novel", "chapter__volume__position", "chapter__position", "position")
    readonly_fields = ("word_count",)
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Content Preview"
