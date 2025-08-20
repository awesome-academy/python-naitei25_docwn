from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from novels.models import Novel, Chapter, Volume
from novels.services.novel_service import NovelService
from constants import ApprovalStatus, ProgressStatus

User = get_user_model()


# -------------------- QUERY TESTS --------------------
class NovelServiceQueryTests(TestCase):
    def setUp(self):
        self.approved_novel = Novel.objects.create(
            name="Approved Novel",
            slug="approved",
            approval_status=ApprovalStatus.APPROVED.value,
        )
        self.pending_novel = Novel.objects.create(
            name="Pending Novel",
            slug="pending",
            approval_status=ApprovalStatus.PENDING.value,
        )

    def test_get_approved_novels(self):
        result = NovelService.get_approved_novels()
        self.assertIn(self.approved_novel, result)
        self.assertNotIn(self.pending_novel, result)

    def test_get_new_novels(self):
        n1 = Novel.objects.create(
            name="Older",
            approval_status=ApprovalStatus.APPROVED.value,
            created_at=timezone.now()
        )
        n2 = Novel.objects.create(
            name="Newer",
            approval_status=ApprovalStatus.APPROVED.value,
            created_at=timezone.now()
        )

        result = list(NovelService.get_new_novels().filter(id__in=[n1.id, n2.id]))

        self.assertEqual(result[0], n2)  
        self.assertEqual(result[1], n1)  

    def test_get_like_novels(self):
        n1 = Novel.objects.create(name="Few Likes", approval_status=ApprovalStatus.APPROVED.value, favorite_count=5)
        n2 = Novel.objects.create(name="Many Likes", approval_status=ApprovalStatus.APPROVED.value, favorite_count=10)
        n3 = Novel.objects.create(name="Approved Novel Zero", approval_status=ApprovalStatus.APPROVED.value, favorite_count=0)
        n4 = Novel.objects.create(name="No Likes", approval_status=ApprovalStatus.APPROVED.value, favorite_count=0)

        result = list(NovelService.get_like_novels())

        # lọc ra novels chỉ thuộc test này
        novels_in_test = [n1, n2, n3, n4]
        result = [n for n in result if n in novels_in_test]

        self.assertEqual(result[:2], [n2, n1])
        self.assertCountEqual(result[2:], [n3, n4])

    def test_get_finished_novels_with_chapters(self):
        finished_with_chapter = Novel.objects.create(
            name="Finished",
            slug="finished",
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.COMPLETED.value,
        )
        volume = Volume.objects.create(
            novel=finished_with_chapter,
            name="Vol 1",
            created_at=timezone.now(),
            position=1,
        )
        Chapter.objects.create(
            volume=volume,
            title="Chapter 1",
            position=1,
        )

        finished_no_chapter = Novel.objects.create(
            name="Finished No Chapter",
            slug="finished-no",
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.COMPLETED.value,
        )
        ongoing = Novel.objects.create(
            name="Ongoing",
            slug="ongoing",
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.ONGOING.value,
        )

        result = list(NovelService.get_finished_novels_with_chapters())
        self.assertEqual(result, [finished_with_chapter])
        self.assertNotIn(finished_no_chapter, result)
        self.assertNotIn(ongoing, result)

    def test_get_recent_volumes_for_cards(self):
        novel = Novel.objects.create(
            name="Novel with Volume",
            approval_status=ApprovalStatus.APPROVED.value,
        )
        volume = Volume.objects.create(
            novel=novel,
            name="Vol 1",
            position=1,
        )
        Chapter.objects.create(
            volume=volume,
            title="Chapter 1",
            approved=True,
            is_hidden=False,
            position=1,
        )

        result = NovelService.get_recent_volumes_for_cards()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], novel.name)
        self.assertEqual(result[0]['slug'], novel.slug)
        self.assertEqual(result[0]['recent_volume']['name'], volume.name)
        self.assertEqual(result[0]['recent_chapter']['title'], "Chapter 1")

# -------------------- APPROVAL / REJECT TESTS --------------------
class NovelServiceApprovalTests(TestCase):
    def setUp(self):
        self.novel = Novel.objects.create(
            name="Pending Novel",
            slug="pending",
            approval_status=ApprovalStatus.PENDING.value,
        )

    def test_approve_novel(self):
        NovelService.approve_novel(self.novel.slug)
        self.novel.refresh_from_db()
        self.assertEqual(self.novel.approval_status, ApprovalStatus.APPROVED.value)

    def test_reject_novel(self):
        NovelService.reject_novel(self.novel.slug, reason="Not suitable")
        self.novel.refresh_from_db()
        self.assertEqual(self.novel.approval_status, ApprovalStatus.REJECTED.value)
        self.assertEqual(self.novel.rejected_reason, "Not suitable")


# -------------------- DETAIL & PAGINATION TESTS --------------------
class NovelServiceDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@test.com",
            password="test123"
        )

    def test_get_novel_detail_owner_can_see_pending(self):
        novel = Novel.objects.create(
            name="Private Novel",
            slug="private",
            approval_status=ApprovalStatus.PENDING.value,
            created_by=self.user,
        )
        result = NovelService.get_novel_detail(novel.slug, user=self.user)
        self.assertEqual(result['novel'], novel)

    def test_get_novel_detail_guest_can_see_approved(self):
        novel = Novel.objects.create(
            name="Public Novel",
            slug="public",
            approval_status=ApprovalStatus.APPROVED.value,
        )
        result = NovelService.get_novel_detail(novel.slug, user=None)
        self.assertEqual(result["novel"], novel)


    def test_volume_pagination_ordering(self):
        novel = Novel.objects.create(
            name="Novel with Volumes",
            slug="novel-vols",
            approval_status=ApprovalStatus.APPROVED.value,
        )
        v1 = Volume.objects.create(
            novel=novel,
            name="Vol 1",
            created_at=timezone.now() - timezone.timedelta(days=1),
            position=1,
        )
        v2 = Volume.objects.create(
            novel=novel,
            name="Vol 2",
            created_at=timezone.now(),
            position=2,
        )

        result = list(novel.volumes.order_by("-created_at"))
        self.assertEqual(result, [v2, v1])
