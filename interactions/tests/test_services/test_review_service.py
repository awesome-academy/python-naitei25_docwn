from django.test import TestCase
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import Http404
from unittest.mock import patch, Mock
from interactions.models import Review
from novels.models import Novel
from accounts.models import User
from interactions.services import ReviewService
from constants import PAGINATOR_REVIEW_LIST, MIN_RATE, MAX_RATE


class TestReviewService(TestCase):
    
    def setUp(self):
        """Setup test data"""
        # Mock objects
        self.mock_novel = Mock(spec=Novel)
        self.mock_novel.slug = 'test-novel'
        
        self.mock_user = Mock(spec=User)
        self.mock_user.pk = 1
        self.mock_user.profile.avatar_url = 'http://example.com/avatar.jpg'
        
        self.mock_review = Mock(spec=Review)
        self.mock_review.rating = 5
        self.mock_review.is_active = True
        
        self.mock_queryset = Mock()
        self.mock_paginator = Mock(spec=Paginator)
        self.mock_page_obj = Mock()
        
    @patch('interactions.services.review_service.get_object_or_404')
    @patch('interactions.services.review_service.ReviewService._get_novel_reviews_queryset')
    @patch('interactions.services.review_service.Paginator')
    def test_get_novel_reviews_data_success(self, mock_paginator_class, mock_get_queryset, mock_get_object):
        """Test get_novel_reviews_data returns correct data"""
        # Setup mocks
        mock_get_object.return_value = self.mock_novel
        mock_get_queryset.return_value = self.mock_queryset
        mock_paginator_instance = Mock()
        mock_paginator_instance.count = 10
        mock_paginator_instance.get_page.return_value = self.mock_page_obj
        mock_paginator_class.return_value = mock_paginator_instance
        
        # Call method
        result = ReviewService.get_novel_reviews_data('test-novel', rating_filter='5', page=2)
        
        # Assertions
        mock_get_object.assert_called_once_with(Novel, slug='test-novel')
        mock_get_queryset.assert_called_once_with(self.mock_novel, '5')
        mock_paginator_class.assert_called_once_with(self.mock_queryset, PAGINATOR_REVIEW_LIST)
        mock_paginator_instance.get_page.assert_called_once_with(2)
        
        expected = {
            'novel': self.mock_novel,
            'page_obj': self.mock_page_obj,
            'rating_filter': '5',
            'total_reviews': 10,
        }
        self.assertEqual(result, expected)
    
    @patch('interactions.services.review_service.get_object_or_404')
    def test_get_novel_reviews_data_novel_not_found(self, mock_get_object):
        """Test get_novel_reviews_data raises Http404 when novel not found"""
        mock_get_object.side_effect = Http404()
        
        with self.assertRaises(Http404):
            ReviewService.get_novel_reviews_data('non-existent-novel')
    
    @patch('interactions.services.review_service.Review.objects')
    def test_get_novel_reviews_queryset_no_filter(self, mock_review_objects):
        """Test _get_novel_reviews_queryset without rating filter"""
        mock_manager = Mock()
        mock_review_objects.select_related.return_value = mock_manager
        mock_manager.filter.return_value = mock_manager
        mock_manager.order_by.return_value = self.mock_queryset
        
        result = ReviewService._get_novel_reviews_queryset(self.mock_novel)
        
        mock_review_objects.select_related.assert_called_once_with('user')
        mock_manager.filter.assert_called_once_with(
            novel=self.mock_novel,
            is_active=True
        )
        mock_manager.order_by.assert_called_once_with('-created_at')
        self.assertEqual(result, self.mock_queryset)
    
    @patch('interactions.services.review_service.Review.objects')
    def test_get_novel_reviews_queryset_with_valid_filter(self, mock_review_objects):
        """Test _get_novel_reviews_queryset with valid rating filter"""
        mock_manager = Mock()
        mock_review_objects.select_related.return_value = mock_manager
        mock_manager.filter.return_value = mock_manager
        mock_manager.order_by.return_value = mock_manager
        
        result = ReviewService._get_novel_reviews_queryset(self.mock_novel, '4')
        
        # Should be called twice: once for base filter, once for rating filter
        self.assertEqual(mock_manager.filter.call_count, 2)
        mock_manager.filter.assert_any_call(novel=self.mock_novel, is_active=True)
        mock_manager.filter.assert_any_call(rating=4)
    
    @patch('interactions.services.review_service.Review.objects')
    def test_get_novel_reviews_queryset_with_invalid_filter(self, mock_review_objects):
        """Test _get_novel_reviews_queryset with invalid rating filter"""
        mock_manager = Mock()
        mock_review_objects.select_related.return_value = mock_manager
        mock_manager.filter.return_value = mock_manager
        mock_manager.order_by.return_value = self.mock_queryset
        
        # Test with invalid string
        result = ReviewService._get_novel_reviews_queryset(self.mock_novel, 'invalid')
        
        # Should only be called once (no rating filter applied)
        mock_manager.filter.assert_called_once_with(
            novel=self.mock_novel,
            is_active=True
        )
        self.assertEqual(result, self.mock_queryset)
    
    @patch('interactions.services.review_service.Review.objects')
    def test_get_novel_reviews_queryset_with_out_of_range_filter(self, mock_review_objects):
        """Test _get_novel_reviews_queryset with out of range rating filter"""
        mock_manager = Mock()
        mock_review_objects.select_related.return_value = mock_manager
        mock_manager.filter.return_value = mock_manager
        mock_manager.order_by.return_value = self.mock_queryset
        
        # Test with rating outside valid range
        result = ReviewService._get_novel_reviews_queryset(self.mock_novel, str(MAX_RATE + 1))
        
        # Should only be called once (no rating filter applied)
        mock_manager.filter.assert_called_once_with(
            novel=self.mock_novel,
            is_active=True
        )
        self.assertEqual(result, self.mock_queryset)
    
    @patch('interactions.services.review_service.get_object_or_404')
    @patch('interactions.services.review_service.Review.objects')
    @patch('interactions.services.review_service.Paginator')
    def test_get_user_reviews_data_success(self, mock_paginator_class, mock_review_objects, mock_get_object):
        """Test get_user_reviews_data returns correct data"""
        # Setup mocks
        mock_get_object.return_value = self.mock_user
        mock_manager = Mock()
        mock_review_objects.select_related.return_value = mock_manager
        mock_manager.filter.return_value = mock_manager
        mock_manager.order_by.return_value = self.mock_queryset
        
        mock_paginator_instance = Mock()
        mock_paginator_instance.get_page.return_value = self.mock_page_obj
        mock_paginator_class.return_value = mock_paginator_instance
        
        # Call method
        result = ReviewService.get_user_reviews_data(1, rating_filter='5', page=2)
        
        # Assertions
        mock_get_object.assert_called_once()
        expected = {
            'reviewed_user': self.mock_user,
            'avatar_url': self.mock_user.profile.avatar_url,
            'page_obj': self.mock_page_obj,
            'rating_filter': '5',
            'rating_choices': range(MIN_RATE + 1, MAX_RATE + 1),
        }
        self.assertEqual(result, expected)
    
    @patch('interactions.services.review_service.Review.objects')
    @patch('interactions.services.review_service.Paginator')
    def test_get_all_reviews_data_with_search_and_filter(self, mock_paginator_class, mock_review_objects):
        """Test get_all_reviews_data with search and rating filter"""
        # Setup mocks
        mock_manager = Mock()
        mock_review_objects.select_related.return_value = mock_manager
        mock_manager.filter.return_value = mock_manager
        mock_manager.order_by.return_value = mock_manager
        
        mock_paginator_instance = Mock()
        mock_paginator_instance.get_page.return_value = self.mock_page_obj
        mock_paginator_class.return_value = mock_paginator_instance
        
        # Call method
        result = ReviewService.get_all_reviews_data(search='test', rating_filter='4', page=1)
        
        # Verify filter was called multiple times (base filter, search filter, rating filter)
        self.assertEqual(mock_manager.filter.call_count, 3)
        
        expected = {
            'page_obj': self.mock_page_obj,
            'search': 'test',
            'rating_filter': '4',
            'rating_choices': range(MIN_RATE + 1, MAX_RATE + 1),
        }
        self.assertEqual(result, expected)
    
    @patch('interactions.services.review_service.get_object_or_404')
    def test_get_review_detail_success(self, mock_get_object):
        """Test get_review_detail returns correct review"""
        mock_get_object.return_value = self.mock_review
        
        result = ReviewService.get_review_detail(1)
        
        mock_get_object.assert_called_once()
        self.assertEqual(result, self.mock_review)
    
    @patch('interactions.services.review_service.get_object_or_404')
    def test_get_review_detail_not_found(self, mock_get_object):
        """Test get_review_detail raises Http404 when review not found"""
        mock_get_object.side_effect = Http404()
        
        with self.assertRaises(Http404):
            ReviewService.get_review_detail(999)
