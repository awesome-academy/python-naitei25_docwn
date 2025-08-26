from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from interactions.models import Request
from constants import RequestStatusChoices
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class RequestModelTest(TestCase):
    def setUp(self):
        """Thiết lập dữ liệu test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
    def test_create_request(self):
        """Test tạo yêu cầu mới"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content for the request',
            status=RequestStatusChoices.PENDING
        )
        
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.title, 'Test Request')
        self.assertEqual(request.content, 'Test content for the request')
        self.assertEqual(request.status, RequestStatusChoices.PENDING)
        self.assertIsNotNone(request.created_at)
        self.assertIsNone(request.processed_at)
        self.assertIsNone(request.processed_by)
        self.assertEqual(request.admin_note, '')
        
    def test_request_str_method(self):
        """Test phương thức __str__ của Request"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content',
            status=RequestStatusChoices.PENDING
        )
        expected = f"Yêu cầu từ {self.user} - Test Request"
        self.assertEqual(str(request), expected)
        
    def test_is_pending_property(self):
        """Test property is_pending"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content',
            status=RequestStatusChoices.PENDING
        )
        self.assertTrue(request.is_pending)
        self.assertFalse(request.is_processed)
        
    def test_is_processed_property(self):
        """Test property is_processed"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content',
            status=RequestStatusChoices.PROCESSED
        )
        self.assertFalse(request.is_pending)
        self.assertTrue(request.is_processed)
        
    def test_mark_processed_method(self):
        """Test phương thức mark_processed"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content',
            status=RequestStatusChoices.PENDING
        )
        
        admin_note = "Request has been reviewed and processed"
        request.mark_processed(self.admin_user, admin_note)
        
        # Refresh from database
        request.refresh_from_db()
        
        self.assertEqual(request.status, RequestStatusChoices.PROCESSED)
        self.assertEqual(request.processed_by, self.admin_user)
        self.assertIsNotNone(request.processed_at)
        self.assertEqual(request.admin_note, admin_note)
        self.assertTrue(request.is_processed)
        self.assertFalse(request.is_pending)
        
    def test_mark_processed_without_note(self):
        """Test mark_processed without admin note"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content',
            status=RequestStatusChoices.PENDING
        )
        
        request.mark_processed(self.admin_user)
        request.refresh_from_db()
        
        self.assertEqual(request.status, RequestStatusChoices.PROCESSED)
        self.assertEqual(request.processed_by, self.admin_user)
        self.assertEqual(request.admin_note, "")
        
    def test_request_ordering(self):
        """Test sắp xếp yêu cầu theo thời gian tạo"""
        # Tạo 3 yêu cầu với thời gian khác nhau
        now = timezone.now()
        
        request1 = Request.objects.create(
            user=self.user,
            title='Request 1',
            content='Content 1'
        )
        
        request2 = Request.objects.create(
            user=self.user,
            title='Request 2',
            content='Content 2'
        )
        
        request3 = Request.objects.create(
            user=self.user,
            title='Request 3',
            content='Content 3'
        )
        
        # Update created_at manually để test ordering
        Request.objects.filter(id=request1.id).update(
            created_at=now - timedelta(hours=2)
        )
        Request.objects.filter(id=request2.id).update(
            created_at=now - timedelta(hours=1)
        )
        Request.objects.filter(id=request3.id).update(
            created_at=now
        )
        
        requests = list(Request.objects.all())
        
        # Should be ordered by -created_at (newest first)
        self.assertEqual(requests[0].id, request3.id)
        self.assertEqual(requests[1].id, request2.id)
        self.assertEqual(requests[2].id, request1.id)
        
    def test_request_indexes(self):
        """Test database indexes"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content'
        )
        
        # Test query với status index
        pending_requests = Request.objects.filter(
            status=RequestStatusChoices.PENDING
        ).order_by('-created_at')
        self.assertIn(request, pending_requests)
        
        # Test query với user index
        user_requests = Request.objects.filter(
            user=self.user
        ).order_by('-created_at')
        self.assertIn(request, user_requests)
        
    def test_request_constraints(self):
        """Test model constraints"""
        # Test required fields
        with self.assertRaises(Exception):
            Request.objects.create(
                title='Test Request',
                content='Test content'
                # Missing user
            )
            
        with self.assertRaises(Exception):
            Request.objects.create(
                user=self.user,
                content='Test content'
                # Missing title
            )
            
        with self.assertRaises(Exception):
            Request.objects.create(
                user=self.user,
                title='Test Request'
                # Missing content
            )
            
    def test_request_max_lengths(self):
        """Test độ dài tối đa của các trường"""
        from constants import MAX_REQUEST_TITLE_LENGTH, MAX_REQUEST_STATUS_LENGTH
        from django.db import transaction, IntegrityError, DataError
        
        # Test title max length
        long_title = 'x' * (MAX_REQUEST_TITLE_LENGTH + 1)
        with self.assertRaises((DataError, IntegrityError)):
            with transaction.atomic():
                Request.objects.create(
                    user=self.user,
                    title=long_title,
                    content='Test content'
                )
            
        # Test valid title length
        valid_title = 'x' * MAX_REQUEST_TITLE_LENGTH
        request = Request.objects.create(
            user=self.user,
            title=valid_title,
            content='Test content'
        )
        self.assertEqual(len(request.title), MAX_REQUEST_TITLE_LENGTH)
        
    def test_request_meta_options(self):
        """Test meta options của model"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content'
        )
        
        # Test verbose_name
        self.assertEqual(request._meta.verbose_name, "Yêu cầu")
        self.assertEqual(request._meta.verbose_name_plural, "Yêu cầu")
        
        # Test default ordering
        self.assertEqual(request._meta.ordering, ['-created_at'])
