from django.test import TestCase
from django.contrib.auth import get_user_model

from novels.models import AuthorRequest, ArtistRequest, Author, Artist
from novels.services import RequestService, AdminRequestService
from novels.forms import AuthorRequestForm, ArtistRequestForm
from constants import ApprovalStatus, Gender

User = get_user_model()


class RequestServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.author_request_data = {
            'name': 'Test Author',
            'pen_name': 'Test Pen Name',
            'description': 'Test description',
            'gender': Gender.MALE.value,
        }

    def test_create_author_request_from_form(self):
        """Test creating author request from form"""
        form = AuthorRequestForm(data=self.author_request_data)
        self.assertTrue(form.is_valid())
        
        author_request = RequestService.create_author_request_from_form(form, self.user)
        
        self.assertEqual(author_request.name, 'Test Author')
        self.assertEqual(author_request.created_by, self.user)
        self.assertEqual(author_request.approval_status, ApprovalStatus.PENDING.value)

    def test_get_user_author_requests(self):
        """Test getting user's author requests"""
        # Create some requests
        AuthorRequest.objects.create(
            name='Author 1',
            created_by=self.user
        )
        AuthorRequest.objects.create(
            name='Author 2',
            created_by=self.user
        )
        
        requests = RequestService.get_user_author_requests(self.user)
        self.assertEqual(requests.count(), 2)

    def test_get_user_author_requests_with_pagination(self):
        """Test getting user's author requests with pagination"""
        # Create some requests
        for i in range(25):
            AuthorRequest.objects.create(
                name=f'Author {i}',
                created_by=self.user
            )
        
        page_obj = RequestService.get_user_author_requests(self.user, page_number=1)
        self.assertEqual(len(page_obj), 10)  # PAGINATOR_COMMON_LIST = 10
        self.assertTrue(page_obj.has_next())

    def test_get_user_author_request(self):
        """Test getting specific user author request"""
        request = AuthorRequest.objects.create(
            name='Test Author',
            created_by=self.user
        )
        
        retrieved_request = RequestService.get_user_author_request(request.pk, self.user)
        self.assertEqual(retrieved_request, request)


class AdminRequestServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        
        self.author_request = AuthorRequest.objects.create(
            name='Test Author',
            pen_name='Test Pen',
            description='Test description',
            gender=Gender.MALE.value,
            created_by=self.user
        )

    def test_get_all_author_requests(self):
        """Test getting all author requests"""
        # Create additional request
        AuthorRequest.objects.create(
            name='Another Author',
            created_by=self.user
        )
        
        requests = AdminRequestService.get_all_author_requests()
        self.assertEqual(requests.count(), 2)

    def test_get_all_author_requests_with_filter(self):
        """Test getting author requests with status filter"""
        # Create approved request
        approved_request = AuthorRequest.objects.create(
            name='Approved Author',
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
        
        requests = AdminRequestService.get_all_author_requests(status_filter=ApprovalStatus.APPROVED.value)
        self.assertEqual(requests.count(), 1)
        self.assertEqual(requests.first(), approved_request)

    def test_approve_author_request_success(self):
        """Test successful author request approval"""
        result = AdminRequestService.approve_author_request(
            self.author_request.pk, 
            self.admin_user
        )
        
        self.assertTrue(result['success'])
        self.assertIn('đã được duyệt thành công', result['message'])
        
        # Check that author was created
        self.author_request.refresh_from_db()
        self.assertEqual(self.author_request.approval_status, ApprovalStatus.APPROVED.value)
        self.assertEqual(self.author_request.approved_by, self.admin_user)
        self.assertIsNotNone(self.author_request.created_author)

    def test_approve_already_approved_request(self):
        """Test approving already approved request"""
        # First approval
        AdminRequestService.approve_author_request(
            self.author_request.pk, 
            self.admin_user
        )
        
        # Second approval attempt
        result = AdminRequestService.approve_author_request(
            self.author_request.pk, 
            self.admin_user
        )
        
        self.assertFalse(result['success'])
        self.assertIn('đã được duyệt trước đó', result['message'])

    def test_reject_author_request_success(self):
        """Test successful author request rejection"""
        reason = "Not qualified"
        result = AdminRequestService.reject_author_request(
            self.author_request.pk, 
            reason
        )
        
        self.assertTrue(result['success'])
        self.assertIn('đã bị từ chối', result['message'])
        
        # Check status was updated
        self.author_request.refresh_from_db()
        self.assertEqual(self.author_request.approval_status, ApprovalStatus.REJECTED.value)
        self.assertEqual(self.author_request.rejected_reason, reason)

    def test_reject_author_request_without_reason(self):
        """Test rejecting author request without reason"""
        result = AdminRequestService.reject_author_request(
            self.author_request.pk, 
            ""
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Vui lòng nhập lý do từ chối', result['message'])

    def test_approve_author_request_updates_novels(self):
        """Test that approving author request updates related novels"""
        from novels.models import Novel
        
        # Create a novel that uses this author request
        novel = Novel.objects.create(
            name='Test Novel',
            summary='Test summary',
            pending_author_request=self.author_request,
            created_by=self.user
        )
        
        # Approve the author request
        result = AdminRequestService.approve_author_request(
            self.author_request.pk, 
            self.admin_user
        )
        
        self.assertTrue(result['success'])
        
        # Check that novel was updated
        novel.refresh_from_db()
        self.author_request.refresh_from_db()
        
        self.assertEqual(novel.author, self.author_request.created_author)
        self.assertIsNone(novel.pending_author_request)
