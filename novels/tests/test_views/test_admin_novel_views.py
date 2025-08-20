"""
Unit tests for Novel Admin Views functionality
"""
from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest.mock import patch, Mock

from novels.models import Novel, Volume, Chapter, Author, Tag
from constants import ApprovalStatus, UserRole
import warnings

warnings.filterwarnings("ignore", message="No directory at:")


User = get_user_model()


class NovelAdminViewTestCase(TestCase):
    """Base test case for novel admin views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.WEBSITE_ADMIN.value
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        # Create test author
        self.author = Author.objects.create(
            name="Test Author",
            description="Test author description"
        )
        
        # Create test novel for approval/rejection testing
        self.pending_novel = Novel.objects.create(
            name="Pending Novel",
            summary="Pending summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value,
            slug="pending-novel"
        )
        
        # Create test novel for list testing
        self.approved_novel = Novel.objects.create(
            name="Approved Novel",
            summary="Approved summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            slug="approved-novel"
        )


class NovelListAdminViewTests(NovelAdminViewTestCase):
    """Test novel list admin view"""
    
    def test_novel_list_admin_access_allowed(self):
        """Test admin can access novel list"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:admin_novels')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('page_obj', response.context)
        # Check if the approved novel appears in paginated results
        novels_in_page = list(response.context['page_obj'])
        self.assertIn(self.approved_novel, novels_in_page)
    
    def test_novel_list_admin_access_denied_for_regular_user(self):
        """Test regular user cannot access admin novel list"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('admin:admin_novels')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
    
    def test_novel_list_admin_access_denied_for_anonymous(self):
        """Test anonymous user cannot access admin novel list"""
        url = reverse('admin:admin_novels')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect to login
    
    def test_novel_list_admin_search(self):
        """Test searching novels by name"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:admin_novels')
        response = self.client.get(url, {'q': 'Approved Novel'})
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        novels_in_page = list(response.context['page_obj'])
        self.assertIn(self.approved_novel, novels_in_page)


class NovelDetailAdminViewTests(NovelAdminViewTestCase):
    """Test novel detail admin view"""
    
    def test_novel_detail_admin_access_allowed(self):
        """Test admin can access novel detail"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:admin_novel_detail', kwargs={'slug': self.approved_novel.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['novel'], self.approved_novel)
    
    def test_novel_detail_admin_access_denied_for_regular_user(self):
        """Test regular user cannot access admin novel detail"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('admin:admin_novel_detail', kwargs={'slug': self.approved_novel.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class NovelApprovalAdminViewTests(NovelAdminViewTestCase):
    """Test novel approval admin views"""
    
    @patch('novels.views.admin.admin_novel_view.NovelService.approve_novel')
    def test_approve_novel_success(self, mock_approve_novel):
        """Test successful novel approval"""
        mock_approve_novel.return_value = {'success': True}
        
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:admin_approve_novel', kwargs={'slug': self.pending_novel.slug})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect after success
        mock_approve_novel.assert_called_once()
    
    @patch('novels.views.admin.admin_novel_view.NovelService.reject_novel')
    def test_reject_novel_success(self, mock_reject_novel):
        """Test successful novel rejection"""
        mock_reject_novel.return_value = self.pending_novel
        
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:admin_reject_novel', kwargs={'slug': self.pending_novel.slug})
        response = self.client.post(url, {
            'rejection_reason': 'Content quality issues'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect after success
        mock_reject_novel.assert_called_once()
    
    def test_approve_novel_permission_denied(self):
        """Test regular user cannot approve novel"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('admin:admin_approve_novel', kwargs={'slug': self.pending_novel.slug})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
    
    def test_reject_novel_permission_denied(self):
        """Test regular user cannot reject novel"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('admin:admin_reject_novel', kwargs={'slug': self.pending_novel.slug})
        response = self.client.post(url, {
            'rejection_reason': 'Test reason'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    @patch('novels.views.admin.admin_novel_view.NovelService.approve_novel')
    def test_approve_novel_author_not_approved(self, mock_approve_novel):
        """Test cannot approve novel when author is not approved"""
        mock_approve_novel.return_value = {'success': False, 'reason': 'author_not_approved'}
        
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:admin_approve_novel', kwargs={'slug': self.pending_novel.slug})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect after failure
        mock_approve_novel.assert_called_once()
        # Check that error message contains information about author not approved
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('tác giả chưa được duyệt' in str(message) for message in messages))
