"""
Unit tests for Admin Request Views
"""
from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest.mock import patch

from novels.models import AuthorRequest, ArtistRequest, Author, Artist, Novel
from constants import ApprovalStatus, UserRole, Gender


User = get_user_model()


class AdminRequestViewTestCase(TestCase):
    """Base test case for admin request views"""
    
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
        
        # Create test author request
        self.author_request = AuthorRequest.objects.create(
            name="Test Author",
            pen_name="Test Pen Name",
            description="Test description",
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        
        # Create test artist request
        self.artist_request = ArtistRequest.objects.create(
            name="Test Artist",
            pen_name="Test Artist Pen Name",
            description="Test artist description",
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )


class AuthorRequestAdminListViewTests(AdminRequestViewTestCase):
    """Test author request admin list view"""
    
    def test_author_request_list_admin_access_allowed(self):
        """Test admin can access author request list"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:author_request_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('page_obj', response.context)
        self.assertContains(response, self.author_request.name)
    
    def test_author_request_list_regular_user_forbidden(self):
        """Test regular user cannot access author request list"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('admin:author_request_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
    
    def test_author_request_list_anonymous_redirect(self):
        """Test anonymous user is redirected to login"""
        url = reverse('admin:author_request_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
    
    def test_author_request_list_filter_by_status(self):
        """Test filtering author requests by status"""
        # Create approved request
        approved_request = AuthorRequest.objects.create(
            name="Approved Author",
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
        
        self.client.login(username='admin@example.com', password='password123')
        
        # Filter by pending status
        url = reverse('admin:author_request_list')
        response = self.client.get(url, {'status': ApprovalStatus.PENDING.value})
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        requests_in_page = list(response.context['page_obj'])
        self.assertIn(self.author_request, requests_in_page)
        self.assertNotIn(approved_request, requests_in_page)


class AuthorRequestAdminDetailViewTests(AdminRequestViewTestCase):
    """Test author request admin detail view"""
    
    def test_author_request_detail_admin_access_allowed(self):
        """Test admin can access author request detail"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:author_request_detail', kwargs={'pk': self.author_request.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['request'], self.author_request)
        self.assertContains(response, self.author_request.name)
    
    def test_author_request_detail_regular_user_forbidden(self):
        """Test regular user cannot access author request detail"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('admin:author_request_detail', kwargs={'pk': self.author_request.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
    
    def test_author_request_detail_nonexistent_request_404(self):
        """Test accessing nonexistent author request returns 404"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:author_request_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class AuthorRequestApprovalViewTests(AdminRequestViewTestCase):
    """Test author request approval view"""
    
    def test_approve_author_request_success(self):
        """Test successful author request approval"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:approve_author_request', kwargs={'pk': self.author_request.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check author request is approved
        self.author_request.refresh_from_db()
        self.assertEqual(self.author_request.approval_status, ApprovalStatus.APPROVED.value)
        self.assertEqual(self.author_request.approved_by, self.admin_user)
        self.assertIsNotNone(self.author_request.created_author)
        
        # Check author is created
        author = self.author_request.created_author
        self.assertEqual(author.name, self.author_request.name)
        self.assertEqual(author.pen_name, self.author_request.pen_name)
        self.assertEqual(author.description, self.author_request.description)
    
    def test_approve_author_request_ajax_success(self):
        """Test successful author request approval via AJAX"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:approve_author_request', kwargs={'pk': self.author_request.pk})
        response = self.client.post(url, HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Check JSON response
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('thành công', response_data['message'])
    
    def test_approve_already_approved_request_warning(self):
        """Test approving already approved request shows warning"""
        # First approve the request
        self.author_request.approval_status = ApprovalStatus.APPROVED.value
        self.author_request.save()
        
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:approve_author_request', kwargs={'pk': self.author_request.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('đã được duyệt trước đó' in str(message) for message in messages))
    
    def test_approve_author_request_with_novels(self):
        """Test approving author request updates related novels"""
        # Create novel using this author request
        novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            summary="Test summary",
            pending_author_request=self.author_request,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:approve_author_request', kwargs={'pk': self.author_request.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check novel is updated
        novel.refresh_from_db()
        self.author_request.refresh_from_db()  # Need to refresh to get created_author
        self.assertEqual(novel.author, self.author_request.created_author)
        self.assertIsNone(novel.pending_author_request)
    
    def test_approve_author_request_regular_user_forbidden(self):
        """Test regular user cannot approve author request"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('admin:approve_author_request', kwargs={'pk': self.author_request.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class AuthorRequestRejectionViewTests(AdminRequestViewTestCase):
    """Test author request rejection view"""
    
    def test_reject_author_request_success(self):
        """Test successful author request rejection"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:reject_author_request', kwargs={'pk': self.author_request.pk})
        response = self.client.post(url, {
            'rejected_reason': 'Insufficient information'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check author request is rejected
        self.author_request.refresh_from_db()
        self.assertEqual(self.author_request.approval_status, ApprovalStatus.REJECTED.value)
        self.assertEqual(self.author_request.rejected_reason, 'Insufficient information')
    
    def test_reject_author_request_no_reason_error(self):
        """Test rejecting author request without reason shows error"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:reject_author_request', kwargs={'pk': self.author_request.pk})
        response = self.client.post(url, {
            'rejected_reason': ''  # Empty reason
        })
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check request is not rejected
        self.author_request.refresh_from_db()
        self.assertEqual(self.author_request.approval_status, ApprovalStatus.PENDING.value)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Vui lòng nhập lý do từ chối' in str(message) for message in messages))
    
    def test_reject_author_request_ajax_success(self):
        """Test successful author request rejection via AJAX"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:reject_author_request', kwargs={'pk': self.author_request.pk})
        response = self.client.post(url, {
            'rejected_reason': 'Insufficient information'
        }, HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Check JSON response
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('từ chối', response_data['message'])


class ArtistRequestAdminListViewTests(AdminRequestViewTestCase):
    """Test artist request admin list view"""
    
    def test_artist_request_list_admin_access_allowed(self):
        """Test admin can access artist request list"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:artist_request_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('page_obj', response.context)
        self.assertContains(response, self.artist_request.name)
    
    def test_artist_request_list_regular_user_forbidden(self):
        """Test regular user cannot access artist request list"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('admin:artist_request_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class ArtistRequestApprovalViewTests(AdminRequestViewTestCase):
    """Test artist request approval view"""
    
    def test_approve_artist_request_success(self):
        """Test successful artist request approval"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:approve_artist_request', kwargs={'pk': self.artist_request.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check artist request is approved
        self.artist_request.refresh_from_db()
        self.assertEqual(self.artist_request.approval_status, ApprovalStatus.APPROVED.value)
        self.assertEqual(self.artist_request.approved_by, self.admin_user)
        self.assertIsNotNone(self.artist_request.created_artist)
        
        # Check artist is created
        artist = self.artist_request.created_artist
        self.assertEqual(artist.name, self.artist_request.name)
        self.assertEqual(artist.pen_name, self.artist_request.pen_name)
        self.assertEqual(artist.description, self.artist_request.description)
    
    def test_approve_artist_request_with_novels(self):
        """Test approving artist request updates related novels"""
        # Create novel using this artist request
        novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            summary="Test summary",
            pending_artist_request=self.artist_request,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:approve_artist_request', kwargs={'pk': self.artist_request.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check novel is updated
        novel.refresh_from_db()
        self.artist_request.refresh_from_db()  # Need to refresh to get created_artist
        self.assertEqual(novel.artist, self.artist_request.created_artist)
        self.assertIsNone(novel.pending_artist_request)


class ArtistRequestRejectionViewTests(AdminRequestViewTestCase):
    """Test artist request rejection view"""
    
    def test_reject_artist_request_success(self):
        """Test successful artist request rejection"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:reject_artist_request', kwargs={'pk': self.artist_request.pk})
        response = self.client.post(url, {
            'rejected_reason': 'Portfolio not sufficient'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check artist request is rejected
        self.artist_request.refresh_from_db()
        self.assertEqual(self.artist_request.approval_status, ApprovalStatus.REJECTED.value)
        self.assertEqual(self.artist_request.rejected_reason, 'Portfolio not sufficient')
    
    def test_reject_artist_request_no_reason_error(self):
        """Test rejecting artist request without reason shows error"""
        self.client.login(username='admin@example.com', password='password123')
        
        url = reverse('admin:reject_artist_request', kwargs={'pk': self.artist_request.pk})
        response = self.client.post(url, {
            'rejected_reason': ''  # Empty reason
        })
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check request is not rejected
        self.artist_request.refresh_from_db()
        self.assertEqual(self.artist_request.approval_status, ApprovalStatus.PENDING.value)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Vui lòng nhập lý do từ chối' in str(message) for message in messages))
