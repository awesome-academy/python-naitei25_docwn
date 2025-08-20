"""
Unit tests for ChapterService functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch

from novels.services.chapter_service import ChapterService
from novels.models import Novel, Volume, Chapter, Author, Chunk
from novels.forms import ChapterForm
from constants import ApprovalStatus, UserRole
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class ChapterServiceTestCase(TestCase):
    """Base test case for ChapterService tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
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
        
        # Create test novel
        self.novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
        
        # Create test volume
        self.volume = Volume.objects.create(
            novel=self.novel,
            name="Test Volume",
            position=1
        )


class ChapterServiceCreationTests(ChapterServiceTestCase):
    """Test ChapterService creation methods"""

    @patch('novels.utils.chunk_manager.ChunkManager.create_html_chunks_for_chapter')
    def test_create_chapter_with_position(self, mock_create_chunks):
        mock_create_chunks.return_value = [
            Mock(content="Test content", word_count=2)
        ]
        Chapter.objects.create(
            volume=self.volume,
            title="Existing Chapter",
            position=1
        )
        chapter_data = {
            'title': 'New Chapter',
            'content': 'New content',
            'volume_choice': str(self.volume.id),
            'position': 2
        }
        form = ChapterForm(novel=self.novel, data=chapter_data)
        chapter = ChapterService.create_chapter(form, self.novel)  # sửa: truyền novel
        self.assertEqual(chapter.position, 2)
        self.assertFalse(chapter.approved)
        self.assertEqual(chapter.title, 'New Chapter')
        self.assertEqual(chapter.volume, self.volume)


class ChapterServiceApprovalTests(ChapterServiceTestCase):
    """Test ChapterService approval methods"""
    
    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.WEBSITE_ADMIN.value
        )
        
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1,
            approved=False
        )
    
    def test_approve_chapter(self):
        """Test approving a chapter"""
        approved_chapter = ChapterService.approve_chapter(
            self.chapter
        )
        self.assertTrue(approved_chapter.approved)
    
    def test_reject_chapter(self):
        """Test rejecting a chapter"""
        rejection_reason = "Content quality issues"
        
        rejected_chapter = ChapterService.reject_chapter(
            self.chapter,
            rejection_reason
        )
        self.assertFalse(rejected_chapter.approved)
        self.assertEqual(rejected_chapter.rejected_reason, rejection_reason)


class ChapterServiceQueryTests(ChapterServiceTestCase):
    """Test ChapterService query methods"""
    
    def setUp(self):
        super().setUp()
        # Create test chapters
        self.approved_chapter = Chapter.objects.create(
            volume=self.volume,
            title="Approved Chapter",
            slug="approved-chapter",
            position=1,
            approved=True,
            is_hidden=False
        )
        
        self.pending_chapter = Chapter.objects.create(
            volume=self.volume,
            title="Pending Chapter",
            slug="pending-chapter",
            position=2,
            approved=False,
            is_hidden=False
        )
        
        self.hidden_chapter = Chapter.objects.create(
            volume=self.volume,
            title="Hidden Chapter",
            slug="hidden-chapter",
            position=3,
            approved=True,
            is_hidden=True
        )

    def test_get_chapter_for_user_public(self):
        """Guest user should only access approved & visible chapters"""
        chapter = ChapterService.get_chapter_for_user(
            chapter_slug=self.approved_chapter.slug,
            novel_slug=self.novel.slug,
            user=None
        )
        self.assertEqual(chapter, self.approved_chapter)

    def test_get_chapter_for_user_owner(self):
        """Owner should access unapproved chapter"""
        chapter = ChapterService.get_chapter_for_user(
            chapter_slug=self.pending_chapter.slug,
            novel_slug=self.novel.slug,
            user=self.user
        )
        self.assertEqual(chapter, self.pending_chapter)

    def test_get_chapter_for_user_not_found(self):
        """Invalid chapter should raise 404"""
        from django.http import Http404
        with self.assertRaises(Http404):
            ChapterService.get_chapter_for_user(
                chapter_slug="non-existent",
                novel_slug=self.novel.slug,
                user=None
            )

    def test_get_all_chapters_for_novel_public(self):
        """Public user sees only approved & visible chapters"""
        chapters = ChapterService.get_all_chapters_for_novel(
            self.novel, user=None
        )
        self.assertIn(self.approved_chapter, chapters)
        self.assertNotIn(self.pending_chapter, chapters)
        self.assertNotIn(self.hidden_chapter, chapters)

    def test_get_all_chapters_for_novel_owner(self):
        """Owner sees all non-deleted chapters"""
        chapters = ChapterService.get_all_chapters_for_novel(
            self.novel, user=self.user
        )
        self.assertIn(self.approved_chapter, chapters)
        self.assertIn(self.pending_chapter, chapters)
        self.assertIn(self.hidden_chapter, chapters)

    def test_get_pending_chapters_for_admin(self):
        """Admin sees pending approval chapters with pagination"""
        page_obj = ChapterService.get_pending_chapters_for_admin(
            search_query="Pending", page=1
        )
        self.assertIn(self.pending_chapter, page_obj.object_list)

    def test_get_earliest_unapproved_chapter(self):
        """Should return the earliest unapproved chapter"""
        earliest = ChapterService.get_earliest_unapproved_chapter(self.novel)
        self.assertEqual(earliest, self.pending_chapter)


class ChapterServiceStatisticsTests(ChapterServiceTestCase):
    """Test ChapterService statistics methods"""
    
    def setUp(self):
        super().setUp()
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1,
            word_count=500
        )
        Chunk.objects.create(chapter=self.chapter, position=1, content="A B C", word_count=3)
        Chunk.objects.create(chapter=self.chapter, position=2, content="D E F G", word_count=4)

    def test_get_chapter_chunks_stats(self):
        """Test chunk statistics"""
        stats = ChapterService.get_chapter_chunks_stats(self.chapter)
        self.assertEqual(stats['total_chunks'], 2)
        self.assertGreater(stats['avg_chunk_size'], 0)
        self.assertGreater(stats['max_chunk_words'], 0)
        self.assertIn('estimated_reading_time', stats)


class ChapterServiceDeleteTests(ChapterServiceTestCase):
    """Test ChapterService deletion methods"""
    
    def setUp(self):
        super().setUp()
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
    
    def test_soft_delete_chapter(self):
        """Test soft deleting chapter"""
        deleted_chapter = ChapterService.soft_delete_chapter(self.chapter)
        self.assertIsNotNone(deleted_chapter.deleted_at)
