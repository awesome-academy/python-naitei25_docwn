from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from http import HTTPStatus
from interactions.models import Review
from novels.models import Novel
from constants import (
    PAGINATOR_REVIEW_LIST,
    MIN_RATE,
    MAX_RATE,
    DEFAULT_PAGE_NUMBER
)


@require_http_methods(["GET"])
def novel_reviews(request, novel_slug):
    try:
        # Lấy novel
        novel = get_object_or_404(Novel, slug=novel_slug)
        
        # Lấy parameters
        page = int(request.GET.get('page', DEFAULT_PAGE_NUMBER))
        rating_filter = request.GET.get('rating', '').strip()
        sort_order = request.GET.get('sort', '-created_at').strip()
        
        # Validate sort order
        valid_sorts = ['-created_at', 'created_at', '-rating', 'rating']
        if sort_order not in valid_sorts:
            sort_order = '-created_at'
        
        # Lấy reviews queryset
        reviews = Review.objects.select_related('user').filter(
            novel=novel,
            is_active=True
        ).order_by(sort_order)
        
        # Áp dụng filter rating
        if rating_filter:
            try:
                rating_value = int(rating_filter)
                if MIN_RATE < rating_value <= MAX_RATE:
                    reviews = reviews.filter(rating=rating_value)
            except (ValueError, TypeError):
                pass
        
        # Pagination
        paginator = Paginator(reviews, PAGINATOR_REVIEW_LIST)
        page_obj = paginator.get_page(page)
        
        # Serialize reviews
        reviews_data = []
        for review in page_obj:
            reviews_data.append({
                'id': review.id,
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.isoformat(),
                'user': {
                    'id': review.user.id,
                    'username': review.user.username,
                    'avatar_url': review.user.profile.get_avatar()
                }
            })
        
        return JsonResponse({
            'success': True,
            'reviews': reviews_data,
            'has_next': page_obj.has_next(),
            'total_reviews': paginator.count,
            'filters': {
                'rating': rating_filter,
                'sort': sort_order,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
