from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from interactions.models import Review
from novels.models import Novel
from constants import (
    PAGINATOR_REVIEW_LIST,
    MIN_RATE,
    MAX_RATE,
)


class ReviewService:
    @staticmethod
    def get_novel_reviews_data(novel_slug, rating_filter=None, page=1):
        # Lấy novel
        novel = get_object_or_404(Novel, slug=novel_slug)
        
        # Lấy reviews cơ bản
        reviews = ReviewService._get_novel_reviews_queryset(novel, rating_filter)
        
        # Phân trang
        paginator = Paginator(reviews, PAGINATOR_REVIEW_LIST)
        page_obj = paginator.get_page(page)
        
        return {
            'novel': novel,
            'page_obj': page_obj,
            'rating_filter': rating_filter,
            'total_reviews': paginator.count,
        }
    
    @staticmethod
    def _get_novel_reviews_queryset(novel, rating_filter=None):
        reviews = Review.objects.select_related('user').filter(
            novel=novel,
            is_active=True
        ).order_by('-created_at')
        
        if rating_filter:
            try:
                rating_value = int(rating_filter)
                if MIN_RATE < rating_value <= MAX_RATE:
                    reviews = reviews.filter(rating=rating_value)
            except (ValueError, TypeError):
                pass  # Ignore invalid rating filter
        
        return reviews
    
    @staticmethod
    def get_user_reviews_data(user_id, rating_filter=None, page=1):
        from accounts.models import User
        
        user = get_object_or_404(User, pk=user_id)
        
        # Lấy reviews
        reviews = Review.objects.select_related('novel').filter(
            user=user,
            is_active=True
        ).order_by('-created_at')
        
        # Lọc theo rating
        if rating_filter:
            try:
                rating_value = int(rating_filter)
                if MIN_RATE < rating_value <= MAX_RATE:
                    reviews = reviews.filter(rating=rating_value)
            except (ValueError, TypeError):
                pass
        
        # Phân trang
        paginator = Paginator(reviews, PAGINATOR_REVIEW_LIST)
        page_obj = paginator.get_page(page)
        
        return {
            'reviewed_user': user,
            'avatar_url': user.profile.avatar_url,
            'page_obj': page_obj,
            'rating_filter': rating_filter,
            'rating_choices': range(MIN_RATE + 1, MAX_RATE + 1),
        }
    
    @staticmethod
    def get_all_reviews_data(search=None, rating_filter=None, page=1):
        reviews = Review.objects.select_related('user', 'novel').filter(
            is_active=True
        ).order_by('-created_at')
        
        # Tìm kiếm
        if search:
            reviews = reviews.filter(
                Q(content__icontains=search) |
                Q(novel__title__icontains=search) |
                Q(user__username__icontains=search)
            )
        
        # Lọc theo rating
        if rating_filter:
            try:
                rating_value = int(rating_filter)
                if MIN_RATE < rating_value <= MAX_RATE:
                    reviews = reviews.filter(rating=rating_value)
            except (ValueError, TypeError):
                pass
        
        # Phân trang
        paginator = Paginator(reviews, PAGINATOR_REVIEW_LIST)
        page_obj = paginator.get_page(page)
        
        return {
            'page_obj': page_obj,
            'search': search,
            'rating_filter': rating_filter,
            'rating_choices': range(MIN_RATE + 1, MAX_RATE + 1),
        }
    
    @staticmethod
    def get_review_detail(review_pk):
        return get_object_or_404(
            Review.objects.select_related('user', 'novel'),
            pk=review_pk,
            is_active=True
        )
