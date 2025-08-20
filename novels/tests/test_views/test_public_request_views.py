"""
Unit tests for Public Request Views
"""
from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages

from novels.models import AuthorRequest, ArtistRequest
from constants import ApprovalStatus, UserRole, Gender


User = get_user_model()


class PublicRequestViewTestCase(TestCase):
    """Base test case for public request views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        # Create another user for testing isolation
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            role=UserRole.USER.value
        )


class AuthorRequestCreateViewTests(PublicRequestViewTestCase):
    """Test author request create view"""
    
    def test_author_request_create_get_authenticated(self):
        """Test GET author request create view when authenticated"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:author_request_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Yêu cầu tạo tác giả mới')
        self.assertIn('form', response.context)
    
    def test_author_request_create_get_anonymous_redirect(self):
        """Test GET author request create view when anonymous redirects to login"""
        url = reverse('novels:author_request_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn('login', response.url)
    
    def test_author_request_create_post_success(self):
        """Test POST author request create with valid data"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:author_request_create')
        form_data = {
            'name': 'Test Author',
            'pen_name': 'Test Pen Name',
            'description': 'Test description',
            'country': 'Vietnam',
        }
        response = self.client.post(url, form_data)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check author request is created
        author_request = AuthorRequest.objects.get(name='Test Author')
        self.assertEqual(author_request.created_by, self.user)
        self.assertEqual(author_request.pen_name, 'Test Pen Name')
        self.assertEqual(author_request.description, 'Test description')
        self.assertEqual(author_request.country, 'Vietnam')
        self.assertEqual(author_request.approval_status, ApprovalStatus.PENDING.value)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('thành công' in str(message) for message in messages))
    
    def test_author_request_create_post_ajax_success(self):
        """Test POST author request create via AJAX"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:author_request_create')
        form_data = {
            'name': 'AJAX Test Author',
            'description': 'AJAX test description',
        }
        response = self.client.post(url, form_data, HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Check JSON response
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('thành công', response_data['message'])
        self.assertIn('request_id', response_data)
        self.assertIn('request_name', response_data)
        
        # Check author request is created
        author_request = AuthorRequest.objects.get(name='AJAX Test Author')
        self.assertEqual(author_request.created_by, self.user)
    
    def test_author_request_create_post_invalid_data(self):
        """Test POST author request create with invalid data"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:author_request_create')
        form_data = {
            'name': '',  # Empty name - invalid
        }
        response = self.client.post(url, form_data)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)  # Form redisplay
        self.assertContains(response, 'form')
        
        # Check no author request is created
        self.assertEqual(AuthorRequest.objects.count(), 0)
    
    def test_author_request_create_post_ajax_invalid_data(self):
        """Test POST author request create via AJAX with invalid data"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:author_request_create')
        form_data = {
            'name': '',  # Empty name - invalid
        }
        response = self.client.post(url, form_data, HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Check JSON response
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)


class ArtistRequestCreateViewTests(PublicRequestViewTestCase):
    """Test artist request create view"""
    
    def test_artist_request_create_get_authenticated(self):
        """Test GET artist request create view when authenticated"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:artist_request_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Yêu cầu tạo họa sĩ mới')
        self.assertIn('form', response.context)
    
    def test_artist_request_create_post_success(self):
        """Test POST artist request create with valid data"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:artist_request_create')
        form_data = {
            'name': 'Test Artist',
            'pen_name': 'Test Artist Pen Name',
            'description': 'Test artist description',
            'country': 'Japan',
            'gender': Gender.FEMALE.value,
        }
        response = self.client.post(url, form_data)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Check artist request is created
        artist_request = ArtistRequest.objects.get(name='Test Artist')
        self.assertEqual(artist_request.created_by, self.user)
        self.assertEqual(artist_request.pen_name, 'Test Artist Pen Name')
        self.assertEqual(artist_request.description, 'Test artist description')
        self.assertEqual(artist_request.country, 'Japan')
        self.assertEqual(artist_request.gender, Gender.FEMALE.value)
        self.assertEqual(artist_request.approval_status, ApprovalStatus.PENDING.value)


class AuthorRequestListViewTests(PublicRequestViewTestCase):
    """Test author request list view"""
    
    def setUp(self):
        super().setUp()
        # Create author requests for different users
        self.user_request = AuthorRequest.objects.create(
            name="User's Author",
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        self.other_user_request = AuthorRequest.objects.create(
            name="Other User's Author",
            created_by=self.other_user,
            approval_status=ApprovalStatus.APPROVED.value
        )
    
    def test_author_request_list_authenticated(self):
        """Test author request list view when authenticated"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:author_request_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('page_obj', response.context)
        
        # Check only user's requests are shown
        requests_in_page = list(response.context['page_obj'])
        self.assertIn(self.user_request, requests_in_page)
        self.assertNotIn(self.other_user_request, requests_in_page)
    
    def test_author_request_list_anonymous_redirect(self):
        """Test author request list view when anonymous redirects to login"""
        url = reverse('novels:author_request_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn('login', response.url)


class ArtistRequestListViewTests(PublicRequestViewTestCase):
    """Test artist request list view"""
    
    def setUp(self):
        super().setUp()
        # Create artist requests for different users
        self.user_request = ArtistRequest.objects.create(
            name="User's Artist",
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        self.other_user_request = ArtistRequest.objects.create(
            name="Other User's Artist",
            created_by=self.other_user,
            approval_status=ApprovalStatus.APPROVED.value
        )
    
    def test_artist_request_list_authenticated(self):
        """Test artist request list view when authenticated"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:artist_request_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('page_obj', response.context)
        
        # Check only user's requests are shown
        requests_in_page = list(response.context['page_obj'])
        self.assertIn(self.user_request, requests_in_page)
        self.assertNotIn(self.other_user_request, requests_in_page)


class AuthorRequestDetailViewTests(PublicRequestViewTestCase):
    """Test author request detail view"""
    
    def setUp(self):
        super().setUp()
        self.user_request = AuthorRequest.objects.create(
            name="User's Author",
            description="Test description",
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        self.other_user_request = AuthorRequest.objects.create(
            name="Other User's Author",
            created_by=self.other_user,
            approval_status=ApprovalStatus.APPROVED.value
        )
    
    def test_author_request_detail_own_request(self):
        """Test viewing own author request detail"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:author_request_detail', kwargs={'pk': self.user_request.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['request'], self.user_request)
        self.assertContains(response, "User&#x27;s Author")  # HTML escaped version
    
    def test_author_request_detail_other_user_request_404(self):
        """Test viewing other user's author request returns 404"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:author_request_detail', kwargs={'pk': self.other_user_request.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    
    def test_author_request_detail_anonymous_redirect(self):
        """Test viewing author request detail when anonymous redirects to login"""
        url = reverse('novels:author_request_detail', kwargs={'pk': self.user_request.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn('login', response.url)


class ArtistRequestDetailViewTests(PublicRequestViewTestCase):
    """Test artist request detail view"""
    
    def setUp(self):
        super().setUp()
        self.user_request = ArtistRequest.objects.create(
            name="User's Artist",
            description="Test artist description",
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        self.other_user_request = ArtistRequest.objects.create(
            name="Other User's Artist",
            created_by=self.other_user,
            approval_status=ApprovalStatus.APPROVED.value
        )
    
    def test_artist_request_detail_own_request(self):
        """Test viewing own artist request detail"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:artist_request_detail', kwargs={'pk': self.user_request.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['request'], self.user_request)
        self.assertContains(response, "User&#x27;s Artist")  # HTML escaped version
    
    def test_artist_request_detail_other_user_request_404(self):
        """Test viewing other user's artist request returns 404"""
        self.client.login(username='test@example.com', password='password123')
        
        url = reverse('novels:artist_request_detail', kwargs={'pk': self.other_user_request.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
