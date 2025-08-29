from constants import UserRole, DATE_FORMAT_DMY, DATE_FORMAT_DMYHI
from novels.models.reading_favorite import Favorite

def user_context(request):
    context = {}
    
    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)
        favorites = Favorite.objects.filter(user=request.user).select_related("novel")
        user_like_novel_count = favorites.count()
        # Get user's novel count
        novel_count = 0
        if hasattr(request.user, 'created_novels'):
            novel_count = request.user.created_novels.filter(deleted_at__isnull=True).count()
        
        context.update({
            'user_profile': user_profile,
            'user_name': request.user.get_name(),
            'user_avatar': user_profile.get_avatar() if user_profile else None,
            'is_admin': request.user.role == UserRole.SYSTEM_ADMIN.value,
            'is_staff': request.user.role in [UserRole.WEBSITE_ADMIN.value, UserRole.SYSTEM_ADMIN.value],
            'user_novel_count': novel_count,
            'user_like_novel_count' : user_like_novel_count,
            'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
            'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        })
    
    return context
