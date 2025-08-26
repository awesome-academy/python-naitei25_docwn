from django.contrib import admin
from .models import Request


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = ['title', 'content', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'processed_at']
    list_per_page = 25
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'content', 'status')
        }),
        ('Xử lý', {
            'fields': ('processed_by', 'admin_note'),
            'classes': ('collapse',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['user']
        return self.readonly_fields
