from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

from novels.models import Novel
from accounts.models import User
from interactions.models import Notification
from constants import UserRole, ApprovalStatus

class NovelCreateNotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Admin user
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            role=UserRole.WEBSITE_ADMIN.value,
        )
        # Regular user
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="password123",
            role=UserRole.USER.value,
        )

    @patch("novels.views.public.novel_view.send_notification_to_user")
    def test_create_pending_novel_triggers_admin_notification(self, mock_send):
        self.client.login(username="user@example.com", password="password123")

        url = reverse("novels:novel_create")
        data = {
            "name": "Test Novel",
            "slug": "test-novel",
            "summary": "This is a test novel"
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # redirect sau khi tạo thành công

        # Kiểm tra novel được tạo
        novel = Novel.objects.get(slug="test-novel")
        self.assertEqual(novel.approval_status, ApprovalStatus.PENDING.value)

        # Kiểm tra notification được tạo cho admin
        notifications = Notification.objects.filter(user=self.admin)
        self.assertEqual(notifications.count(), 1)
        notif = notifications.first()
        self.assertIn("Test Novel", notif.content)

        # Kiểm tra hàm send_notification_to_user được gọi
        mock_send.assert_called_once()
        call_args = mock_send.call_args[1]  # lấy kwargs
        self.assertEqual(call_args["user_id"], self.admin.id)
        self.assertEqual(call_args["notification"].related_object, novel)
