"""
Unit tests for Search Novels public view
"""
from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse

from novels.models import Novel, Author, Tag
from constants import ApprovalStatus, ProgressStatus, SEARCH_RESULTS_LIMIT, DEFAULT_RATING_AVERAGE

class SearchNovelsViewTestCase(TestCase):
    """Base setup for search novels view tests"""

    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name="Author A")
        self.author_b = Author.objects.create(name="Author B")

        # Create some novels
        self.novel1 = Novel.objects.create(
            name="Alpha Novel",
            slug="alpha-novel",
            author=self.author,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.ONGOING.value,
        )
        self.novel2 = Novel.objects.create(
            name="Beta Novel",
            slug="beta-novel",
            author=self.author,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.COMPLETED.value,
        )
        self.novel3 = Novel.objects.create(
            name="Gamma Novel",
            slug="gamma-novel",
            author=self.author_b,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.SUSPEND.value,
        )
        self.tag_action = Tag.objects.create(name="Action", slug="action")
        self.tag_drama = Tag.objects.create(name="Drama", slug="drama")
        self.novel1.tags.add(self.tag_action)
        self.novel2.tags.add(self.tag_drama)
        self.novel3.tags.add(self.tag_action, self.tag_drama)
        self.url = reverse("novels:search_novels")

class SearchNovelsBasicTests(SearchNovelsViewTestCase):
    """Test search novels without filters"""

    def test_search_without_params(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.content.decode()
        self.assertIn("Alpha Novel", content)
        self.assertIn("Beta Novel", content)

    def test_search_by_keyword(self):
        response = self.client.get(self.url, {"q": "Alpha"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.content.decode()
        self.assertIn("Alpha Novel", content)
        self.assertNotIn("Beta Novel", content)
    
    def test_empty_result(self):
        """Query with no matching novels should show empty result"""
        response = self.client.get(self.url, {"q": "Nonexistent"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.content.decode()
        self.assertNotIn("Alpha Novel", content)
        self.assertNotIn("Beta Novel", content)
        self.assertNotIn("Gamma Novel", content)
        self.assertIn("Không tìm thấy kết quả", content)


class SearchNovelsFilterTests(SearchNovelsViewTestCase):
    """Test search novels with filters"""

    def test_filter_by_status(self):
        response = self.client.get(self.url, {"status": ProgressStatus.ONGOING.value})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.content.decode()
        self.assertIn("Alpha Novel", content)
        self.assertNotIn("Beta Novel", content)

    def test_filter_by_author(self):
        response = self.client.get(self.url, {"author": "Author A"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.content.decode()
        self.assertIn("Alpha Novel", content)
        self.assertIn("Beta Novel", content)

    def test_filter_by_tag(self):
        response = self.client.get(self.url, {"tags": [self.tag_action.slug]})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.content.decode()
        self.assertIn("Alpha Novel", content)
        self.assertNotIn("Beta Novel", content)

    def test_filter_combined(self):
        response = self.client.get(self.url, {"author": "Author B", "tags": [self.tag_drama.slug]})
        content = response.content.decode()
        self.assertIn("Gamma Novel", content)
        self.assertNotIn("Alpha Novel", content)
        self.assertNotIn("Beta Novel", content)


class SearchNovelsSortTests(SearchNovelsViewTestCase):
    """Test search novels sorting"""

    def test_sort_by_updated(self):
        response = self.client.get(self.url, {"sort": "updated"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Chỉ cần đảm bảo không lỗi, không cần kiểm tra thứ tự cụ thể

    def test_sort_by_rating(self):
        response = self.client.get(self.url, {"sort": "rating"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Tránh lỗi 'Cannot reorder a query once a slice has been taken'

class SearchNovelsPopularTests(SearchNovelsViewTestCase):
    """Popular novels when query is empty"""

    def test_popular_novels_displayed(self):
        response = self.client.get(self.url)
        content = response.content.decode()
        # Check at least one novel appears in popular section
        self.assertIn("Alpha Novel", content)
        self.assertIn("Beta Novel", content)
