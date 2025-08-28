from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
from interactions.services import RequestService
from interactions.models import Request
from constants import RequestStatusChoices, RequestSortChoices
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class RequestServiceTest(TestCase):
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
        
    def test_create_request_success(self):
        """Test tạo yêu cầu thành công"""
        result = RequestService.create_request(
            user=self.user,
            title='Test Request',
            content='Test content for the request'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('request', result)
        self.assertIn('message', result)
        
        request = result['request']
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.title, 'Test Request')
        self.assertEqual(request.content, 'Test content for the request')
        self.assertEqual(request.status, RequestStatusChoices.PENDING)
        
    def test_create_request_strips_whitespace(self):
        """Test tạo yêu cầu tự động loại bỏ khoảng trắng"""
        result = RequestService.create_request(
            user=self.user,
            title='  Test Request  ',
            content='  Test content  '
        )
        
        self.assertTrue(result['success'])
        request = result['request']
        self.assertEqual(request.title, 'Test Request')
        self.assertEqual(request.content, 'Test content')
        
    def test_get_user_requests_basic(self):
        """Test lấy danh sách yêu cầu cơ bản"""
        # Tạo một số yêu cầu
        for i in range(5):
            Request.objects.create(
                user=self.user,
                title=f'Request {i}',
                content=f'Content {i}'
            )
            
        result = RequestService.get_user_requests(user=self.user)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 5)
        self.assertEqual(len(result['requests']), 5)
        
    def test_get_user_requests_pagination(self):
        """Test phân trang yêu cầu"""
        # Tạo 15 yêu cầu
        for i in range(15):
            Request.objects.create(
                user=self.user,
                title=f'Request {i}',
                content=f'Content {i}'
            )
            
        # Test trang 1
        result = RequestService.get_user_requests(
            user=self.user,
            page=1,
            per_page=10
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 15)
        self.assertEqual(len(result['requests']), 10)
        
        # Test trang 2
        result = RequestService.get_user_requests(
            user=self.user,
            page=2,
            per_page=10
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['requests']), 5)
        
    def test_get_user_requests_status_filter(self):
        """Test lọc yêu cầu theo trạng thái"""
        # Tạo yêu cầu với trạng thái khác nhau
        pending_request = Request.objects.create(
            user=self.user,
            title='Pending Request',
            content='Pending content',
            status=RequestStatusChoices.PENDING
        )
        
        processed_request = Request.objects.create(
            user=self.user,
            title='Processed Request',
            content='Processed content',
            status=RequestStatusChoices.PROCESSED
        )
        
        # Test lọc pending
        result = RequestService.get_user_requests(
            user=self.user,
            status_filter=RequestStatusChoices.PENDING
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 1)
        self.assertEqual(result['requests'][0].id, pending_request.id)
        
        # Test lọc processed
        result = RequestService.get_user_requests(
            user=self.user,
            status_filter=RequestStatusChoices.PROCESSED
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 1)
        self.assertEqual(result['requests'][0].id, processed_request.id)
        
    def test_get_user_requests_search(self):
        """Test tìm kiếm yêu cầu"""
        Request.objects.create(
            user=self.user,
            title='Bug Report',
            content='There is a bug in the system'
        )
        
        Request.objects.create(
            user=self.user,
            title='Feature Request',
            content='Please add new feature'
        )
        
        # Tìm theo title
        result = RequestService.get_user_requests(
            user=self.user,
            search='Bug'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 1)
        self.assertIn('Bug', result['requests'][0].title)
        
        # Tìm theo content
        result = RequestService.get_user_requests(
            user=self.user,
            search='feature'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 1)
        self.assertIn('Feature', result['requests'][0].title)
        
    def test_get_user_requests_sorting(self):
        """Test sắp xếp yêu cầu"""
        now = timezone.now()
        
        # Tạo yêu cầu với thời gian khác nhau
        request1 = Request.objects.create(
            user=self.user,
            title='A Request',
            content='Content 1'
        )
        
        request2 = Request.objects.create(
            user=self.user,
            title='B Request',
            content='Content 2'
        )
        
        # Update thời gian tạo
        Request.objects.filter(id=request1.id).update(
            created_at=now - timedelta(hours=1)
        )
        Request.objects.filter(id=request2.id).update(
            created_at=now
        )
        
        # Test sắp xếp theo ngày tạo mới nhất
        result = RequestService.get_user_requests(
            user=self.user,
            sort_by=RequestSortChoices.CREATED_DESC
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['requests'][0].id, request2.id)
        self.assertEqual(result['requests'][1].id, request1.id)
        
        # Test sắp xếp theo title A-Z
        result = RequestService.get_user_requests(
            user=self.user,
            sort_by=RequestSortChoices.TITLE_ASC
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['requests'][0].id, request1.id)
        self.assertEqual(result['requests'][1].id, request2.id)
        
    def test_get_all_requests_for_admin_basic(self):
        """Test admin lấy tất cả yêu cầu"""
        # Tạo yêu cầu từ nhiều user
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        Request.objects.create(
            user=self.user,
            title='Request 1',
            content='Content 1'
        )
        
        Request.objects.create(
            user=user2,
            title='Request 2',
            content='Content 2'
        )
        
        result = RequestService.get_all_requests_for_admin()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 2)
        
    def test_get_all_requests_for_admin_advanced_filters(self):
        """Test admin lọc nâng cao"""
        # Tạo user khác
        user2 = User.objects.create_user(
            username='searchuser',
            email='search@example.com',
            password='pass123'
        )
        
        # Tạo yêu cầu để test
        request1 = Request.objects.create(
            user=self.user,
            title='Bug Report',
            content='System bug found'
        )
        
        request2 = Request.objects.create(
            user=user2,
            title='Feature Request',
            content='New feature needed'
        )
        
        # Test tìm kiếm theo username
        result = RequestService.get_all_requests_for_admin(
            user_filter='searchuser'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 1)
        self.assertEqual(result['requests'][0].id, request2.id)
        
        # Test tìm kiếm theo email
        result = RequestService.get_all_requests_for_admin(
            user_filter='search@'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 1)
        
    def test_get_all_requests_for_admin_date_filter(self):
        """Test admin lọc theo ngày"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Tạo yêu cầu hôm qua
        request_yesterday = Request.objects.create(
            user=self.user,
            title='Yesterday Request',
            content='Content yesterday'
        )
        
        # Tạo yêu cầu hôm nay
        request_today = Request.objects.create(
            user=self.user,
            title='Today Request',
            content='Content today'
        )
        
        # Update ngày tạo - đảm bảo timezone đúng
        yesterday_datetime = timezone.make_aware(
            datetime.combine(yesterday, datetime.min.time())
        )
        Request.objects.filter(id=request_yesterday.id).update(
            created_at=yesterday_datetime
        )
        
        # Test lọc từ ngày hôm nay
        result = RequestService.get_all_requests_for_admin(
            date_from=today.strftime('%Y-%m-%d')
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 1)
        self.assertEqual(result['requests'][0].id, request_today.id)
        
        # Test lọc đến ngày hôm qua
        result = RequestService.get_all_requests_for_admin(
            date_to=yesterday.strftime('%Y-%m-%d')
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_count'], 1)
        self.assertEqual(result['requests'][0].id, request_yesterday.id)
        
    def test_get_request_detail_success(self):
        """Test lấy chi tiết yêu cầu thành công"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content'
        )
        
        result = RequestService.get_request_detail(request.id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['request'].id, request.id)
        
    def test_get_request_detail_not_found(self):
        """Test lấy chi tiết yêu cầu không tồn tại"""
        result = RequestService.get_request_detail(999)
        
        self.assertFalse(result['success'])
        self.assertIn('message', result)
        
    def test_get_request_detail_permission(self):
        """Test quyền truy cập chi tiết yêu cầu"""
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        request = Request.objects.create(
            user=self.user,
            title='Private Request',
            content='Private content'
        )
        
        # User khác không thể xem
        result = RequestService.get_request_detail(request.id, user2)
        
        self.assertFalse(result['success'])
        self.assertIn('không có quyền', result['message'])
        
        # Owner có thể xem
        result = RequestService.get_request_detail(request.id, self.user)
        
        self.assertTrue(result['success'])
        
        # Admin có thể xem
        result = RequestService.get_request_detail(request.id, self.admin_user)
        
        self.assertTrue(result['success'])
        
    def test_process_request_success(self):
        """Test xử lý yêu cầu thành công"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content',
            status=RequestStatusChoices.PENDING
        )
        
        admin_note = "Request processed successfully"
        result = RequestService.process_request(
            request.id,
            self.admin_user,
            admin_note
        )
        
        self.assertTrue(result['success'])
        
        # Refresh từ database
        request.refresh_from_db()
        self.assertEqual(request.status, RequestStatusChoices.PROCESSED)
        self.assertEqual(request.processed_by, self.admin_user)
        self.assertEqual(request.admin_note, admin_note)
        self.assertIsNotNone(request.processed_at)
        
    def test_process_request_already_processed(self):
        """Test xử lý yêu cầu đã được xử lý"""
        request = Request.objects.create(
            user=self.user,
            title='Test Request',
            content='Test content',
            status=RequestStatusChoices.PROCESSED
        )
        
        result = RequestService.process_request(
            request.id,
            self.admin_user,
            "Try to process again"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('đã được xử lý', result['message'])
        
    def test_process_request_not_found(self):
        """Test xử lý yêu cầu không tồn tại"""
        result = RequestService.process_request(
            999,
            self.admin_user,
            "Note"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Không tìm thấy', result['message'])
