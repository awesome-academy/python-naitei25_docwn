"""
Unit tests for ArtistRequest model
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta

from novels.models import ArtistRequest, Artist
from constants import ApprovalStatus, Gender, UserRole


User = get_user_model()


class ArtistRequestModelTestCase(TestCase):
    """Base test case for ArtistRequest model tests"""
    
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


class ArtistRequestModelCreationTests(ArtistRequestModelTestCase):
    """Test ArtistRequest model creation"""
    
    def test_create_artist_request_minimal(self):
        """Test creating artist request with minimal required fields"""
        artist_request = ArtistRequest.objects.create(
            name="Test Artist",
            created_by=self.user
        )
        
        self.assertEqual(artist_request.name, "Test Artist")
        self.assertEqual(artist_request.created_by, self.user)
        self.assertEqual(artist_request.approval_status, ApprovalStatus.PENDING.value)
        self.assertIsNone(artist_request.pen_name)
        self.assertIsNone(artist_request.description)
        self.assertIsNone(artist_request.approved_by)
        self.assertIsNone(artist_request.created_artist)
        self.assertIsNotNone(artist_request.created_at)
        self.assertIsNotNone(artist_request.updated_at)
    
    def test_create_artist_request_full(self):
        """Test creating artist request with all fields"""
        birthday = date(1980, 1, 1)
        deathday = date(2020, 12, 31)
        
        artist_request = ArtistRequest.objects.create(
            name="Full Test Artist",
            pen_name="Test Pen Name",
            description="Test description",
            birthday=birthday,
            deathday=deathday,
            gender=Gender.FEMALE.value,
            country="Japan",
            image_url="https://example.com/image.jpg",
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            approved_by=self.admin_user
        )
        
        self.assertEqual(artist_request.name, "Full Test Artist")
        self.assertEqual(artist_request.pen_name, "Test Pen Name")
        self.assertEqual(artist_request.description, "Test description")
        self.assertEqual(artist_request.birthday, birthday)
        self.assertEqual(artist_request.deathday, deathday)
        self.assertEqual(artist_request.gender, Gender.FEMALE.value)
        self.assertEqual(artist_request.country, "Japan")
        self.assertEqual(artist_request.image_url, "https://example.com/image.jpg")
        self.assertEqual(artist_request.created_by, self.user)
        self.assertEqual(artist_request.approval_status, ApprovalStatus.APPROVED.value)
        self.assertEqual(artist_request.approved_by, self.admin_user)


class ArtistRequestModelMethodTests(ArtistRequestModelTestCase):
    """Test ArtistRequest model methods"""
    
    def setUp(self):
        super().setUp()
        self.artist_request = ArtistRequest.objects.create(
            name="Test Artist",
            pen_name="Test Pen Name",
            created_by=self.user
        )
    
    def test_str_method(self):
        """Test string representation"""
        expected = f"Artist Request: {self.artist_request.name} by {self.user.username}"
        self.assertEqual(str(self.artist_request), expected)
    
    def test_get_display_name_with_pen_name(self):
        """Test get_display_name when pen_name exists"""
        self.assertEqual(self.artist_request.get_display_name(), "Test Pen Name")
    
    def test_get_display_name_without_pen_name(self):
        """Test get_display_name when pen_name is None"""
        self.artist_request.pen_name = None
        self.artist_request.save()
        self.assertEqual(self.artist_request.get_display_name(), "Test Artist")
    
    def test_get_display_name_with_empty_pen_name(self):
        """Test get_display_name when pen_name is empty"""
        self.artist_request.pen_name = ""
        self.artist_request.save()
        self.assertEqual(self.artist_request.get_display_name(), "Test Artist")
    
    def test_can_be_used_in_novel_pending(self):
        """Test can_be_used_in_novel for pending request"""
        self.artist_request.approval_status = ApprovalStatus.PENDING.value
        self.artist_request.save()
        self.assertTrue(self.artist_request.can_be_used_in_novel())
    
    def test_can_be_used_in_novel_approved(self):
        """Test can_be_used_in_novel for approved request"""
        self.artist_request.approval_status = ApprovalStatus.APPROVED.value
        self.artist_request.save()
        self.assertTrue(self.artist_request.can_be_used_in_novel())
    
    def test_can_be_used_in_novel_rejected(self):
        """Test can_be_used_in_novel for rejected request"""
        self.artist_request.approval_status = ApprovalStatus.REJECTED.value
        self.artist_request.save()
        self.assertFalse(self.artist_request.can_be_used_in_novel())
    
    def test_can_be_used_in_novel_draft(self):
        """Test can_be_used_in_novel for draft request"""
        self.artist_request.approval_status = ApprovalStatus.DRAFT.value
        self.artist_request.save()
        self.assertFalse(self.artist_request.can_be_used_in_novel())


class ArtistRequestModelRelationshipTests(ArtistRequestModelTestCase):
    """Test ArtistRequest model relationships"""
    
    def test_created_by_relationship(self):
        """Test created_by foreign key relationship"""
        artist_request = ArtistRequest.objects.create(
            name="Test Artist",
            created_by=self.user
        )
        
        self.assertEqual(artist_request.created_by, self.user)
        self.assertIn(artist_request, self.user.artist_requests.all())
    
    def test_approved_by_relationship(self):
        """Test approved_by foreign key relationship"""
        artist_request = ArtistRequest.objects.create(
            name="Test Artist",
            created_by=self.user,
            approved_by=self.admin_user
        )
        
        self.assertEqual(artist_request.approved_by, self.admin_user)
        self.assertIn(artist_request, self.admin_user.approved_artist_requests.all())
    
    def test_created_artist_relationship(self):
        """Test created_artist one-to-one relationship"""
        # Create artist first
        artist = Artist.objects.create(
            name="Test Artist",
            description="Test description"
        )
        
        # Create artist request and link to artist
        artist_request = ArtistRequest.objects.create(
            name="Test Artist",
            created_by=self.user,
            created_artist=artist
        )
        
        self.assertEqual(artist_request.created_artist, artist)
        self.assertEqual(artist.source_request, artist_request)


class ArtistRequestModelIndexTests(ArtistRequestModelTestCase):
    """Test ArtistRequest model database indexes"""
    
    def test_model_indexes_exist(self):
        """Test that model has expected indexes"""
        indexes = ArtistRequest._meta.indexes
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


class ArtistRequestModelVerboseNameTests(ArtistRequestModelTestCase):
    """Test ArtistRequest model verbose names"""
    
    def test_verbose_names(self):
        """Test model verbose names"""
        self.assertEqual(ArtistRequest._meta.verbose_name, "Artist Request")
        self.assertEqual(ArtistRequest._meta.verbose_name_plural, "Artist Requests")


class ArtistRequestModelConstraintTests(ArtistRequestModelTestCase):
    """Test ArtistRequest model constraints and validation"""
    
    def test_approval_status_choices(self):
        """Test approval_status field choices"""
        artist_request = ArtistRequest.objects.create(
            name="Test Artist",
            created_by=self.user
        )
        
        # Test valid choices
        valid_statuses = [status.value for status in ApprovalStatus]
        for status in valid_statuses:
            artist_request.approval_status = status
            artist_request.save()  # Should not raise exception
    
    def test_gender_choices(self):
        """Test gender field choices"""
        artist_request = ArtistRequest.objects.create(
            name="Test Artist",
            created_by=self.user
        )
        
        # Test valid choices
        valid_genders = [gender.value for gender in Gender]
        for gender in valid_genders:
            artist_request.gender = gender
            artist_request.save()  # Should not raise exception
        
        # Test None is allowed
        artist_request.gender = None
        artist_request.save()  # Should not raise exception
