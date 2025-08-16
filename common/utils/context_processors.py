from constants import UserRole

def user_context(request):
    context = {}
    
    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)
        
        # Get user's novel count
        novel_count = 0
        if hasattr(request.user, 'created_novels'):
            novel_count = request.user.created_novels.filter(deleted_at__isnull=True).count()
        
        context.update({
            'user_profile': user_profile,
            'user_name': request.user.get_name(),
            'user_avatar': user_profile.avatar if user_profile and user_profile.avatar else None,
            'is_admin': request.user.role == UserRole.SYSTEM_ADMIN.value,
            'is_staff': request.user.role in [UserRole.WEBSITE_ADMIN.value, UserRole.SYSTEM_ADMIN.value],
            'user_novel_count': novel_count,
        })
    
    return context
