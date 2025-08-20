"""
Unit tests for AuthorRequest model
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta

from novels.models import AuthorRequest, Author
from constants import ApprovalStatus, Gender, UserRole


User = get_user_model()


class AuthorRequestModelTestCase(TestCase):
    """Base test case for AuthorRequest model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.WEBSITE_ADMIN.value
        )


class AuthorRequestModelCreationTests(AuthorRequestModelTestCase):
    """Test AuthorRequest model creation"""
    
    def test_create_author_request_minimal(self):
        """Test creating author request with minimal required fields"""
        author_request = AuthorRequest.objects.create(
            name="Test Author",
            created_by=self.user
        )
        
        self.assertEqual(author_request.name, "Test Author")
        self.assertEqual(author_request.created_by, self.user)
        self.assertEqual(author_request.approval_status, ApprovalStatus.PENDING.value)
        self.assertIsNone(author_request.pen_name)
        self.assertIsNone(author_request.description)
        self.assertIsNone(author_request.approved_by)
        self.assertIsNone(author_request.created_author)
        self.assertIsNotNone(author_request.created_at)
        self.assertIsNotNone(author_request.updated_at)
    
    def test_create_author_request_full(self):
        """Test creating author request with all fields"""
        birthday = date(1980, 1, 1)
        deathday = date(2020, 12, 31)
        
        author_request = AuthorRequest.objects.create(
            name="Full Test Author",
            pen_name="Test Pen Name",
            description="Test description",
            birthday=birthday,
            deathday=deathday,
            gender=Gender.MALE.value,
            country="Vietnam",
            image_url="https://example.com/image.jpg",
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            approved_by=self.admin_user
        )
        
        self.assertEqual(author_request.name, "Full Test Author")
        self.assertEqual(author_request.pen_name, "Test Pen Name")
        self.assertEqual(author_request.description, "Test description")
        self.assertEqual(author_request.birthday, birthday)
        self.assertEqual(author_request.deathday, deathday)
        self.assertEqual(author_request.gender, Gender.MALE.value)
        self.assertEqual(author_request.country, "Vietnam")
        self.assertEqual(author_request.image_url, "https://example.com/image.jpg")
        self.assertEqual(author_request.created_by, self.user)
        self.assertEqual(author_request.approval_status, ApprovalStatus.APPROVED.value)
        self.assertEqual(author_request.approved_by, self.admin_user)


class AuthorRequestModelMethodTests(AuthorRequestModelTestCase):
    """Test AuthorRequest model methods"""
    
    def setUp(self):
        super().setUp()
        self.author_request = AuthorRequest.objects.create(
            name="Test Author",
            pen_name="Test Pen Name",
            created_by=self.user
        )
    
    def test_str_method(self):
        """Test string representation"""
        expected = f"Author Request: {self.author_request.name} by {self.user.username}"
        self.assertEqual(str(self.author_request), expected)
    
    def test_get_display_name_with_pen_name(self):
        """Test get_display_name when pen_name exists"""
        self.assertEqual(self.author_request.get_display_name(), "Test Pen Name")
    
    def test_get_display_name_without_pen_name(self):
        """Test get_display_name when pen_name is None"""
        self.author_request.pen_name = None
        self.author_request.save()
        self.assertEqual(self.author_request.get_display_name(), "Test Author")
    
    def test_get_display_name_with_empty_pen_name(self):
        """Test get_display_name when pen_name is empty"""
        self.author_request.pen_name = ""
        self.author_request.save()
        self.assertEqual(self.author_request.get_display_name(), "Test Author")
    
    def test_can_be_used_in_novel_pending(self):
        """Test can_be_used_in_novel for pending request"""
        self.author_request.approval_status = ApprovalStatus.PENDING.value
        self.author_request.save()
        self.assertTrue(self.author_request.can_be_used_in_novel())
    
    def test_can_be_used_in_novel_approved(self):
        """Test can_be_used_in_novel for approved request"""
        self.author_request.approval_status = ApprovalStatus.APPROVED.value
        self.author_request.save()
        self.assertTrue(self.author_request.can_be_used_in_novel())
    
    def test_can_be_used_in_novel_rejected(self):
        """Test can_be_used_in_novel for rejected request"""
        self.author_request.approval_status = ApprovalStatus.REJECTED.value
        self.author_request.save()
        self.assertFalse(self.author_request.can_be_used_in_novel())
    
    def test_can_be_used_in_novel_draft(self):
        """Test can_be_used_in_novel for draft request"""
        self.author_request.approval_status = ApprovalStatus.DRAFT.value
        self.author_request.save()
        self.assertFalse(self.author_request.can_be_used_in_novel())


class AuthorRequestModelRelationshipTests(AuthorRequestModelTestCase):
    """Test AuthorRequest model relationships"""
    
    def test_created_by_relationship(self):
        """Test created_by foreign key relationship"""
        author_request = AuthorRequest.objects.create(
            name="Test Author",
            created_by=self.user
        )
        
        self.assertEqual(author_request.created_by, self.user)
        self.assertIn(author_request, self.user.author_requests.all())
    
    def test_approved_by_relationship(self):
        """Test approved_by foreign key relationship"""
        author_request = AuthorRequest.objects.create(
            name="Test Author",
            created_by=self.user,
            approved_by=self.admin_user
        )
        
        self.assertEqual(author_request.approved_by, self.admin_user)
        self.assertIn(author_request, self.admin_user.approved_author_requests.all())
    
    def test_created_author_relationship(self):
        """Test created_author one-to-one relationship"""
        # Create author first
        author = Author.objects.create(
            name="Test Author",
            description="Test description"
        )
        
        # Create author request and link to author
        author_request = AuthorRequest.objects.create(
            name="Test Author",
            created_by=self.user,
            created_author=author
        )
        
        self.assertEqual(author_request.created_author, author)
        self.assertEqual(author.source_request, author_request)


class AuthorRequestModelIndexTests(AuthorRequestModelTestCase):
    """Test AuthorRequest model database indexes"""
    
    def test_model_indexes_exist(self):
        """Test that model has expected indexes"""
        indexes = AuthorRequest._meta.indexes
        self.assertEqual(len(indexes), 3)
        
        # Check index field names
        index_fields = [list(index.fields) for index in indexes]
        
        expected_indexes = [
            ['created_by', '-created_at'],
            ['approval_status', '-created_at'],
            ['name']
        ]
        
        for expected_index in expected_indexes:
            self.assertIn(expected_index, index_fields)


class AuthorRequestModelVerboseNameTests(AuthorRequestModelTestCase):
    """Test AuthorRequest model verbose names"""
    
    def test_verbose_names(self):
        """Test model verbose names"""
        self.assertEqual(AuthorRequest._meta.verbose_name, "Author Request")
        self.assertEqual(AuthorRequest._meta.verbose_name_plural, "Author Requests")


class AuthorRequestModelConstraintTests(AuthorRequestModelTestCase):
    """Test AuthorRequest model constraints and validation"""
    
    def test_approval_status_choices(self):
        """Test approval_status field choices"""
        author_request = AuthorRequest.objects.create(
            name="Test Author",
            created_by=self.user
        )
        
        # Test valid choices
        valid_statuses = [status.value for status in ApprovalStatus]
        for status in valid_statuses:
            author_request.approval_status = status
            author_request.save()  # Should not raise exception
    
    def test_gender_choices(self):
        """Test gender field choices"""
        author_request = AuthorRequest.objects.create(
            name="Test Author",
            created_by=self.user
        )
        
        # Test valid choices
        valid_genders = [gender.value for gender in Gender]
        for gender in valid_genders:
            author_request.gender = gender
            author_request.save()  # Should not raise exception
        
        # Test None is allowed
        author_request.gender = None
        author_request.save()  # Should not raise exception
