from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch
from interactions.models.comment import Comment
from interactions.views.public.comment_view import notify_user_reply_comment
from novels.models.novel import Novel

User = get_user_model()

class NotifyUserReplyCommentTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="123"
        )

        self.novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel"
        )
        self.parent_comment = Comment.objects.create(
            novel=self.novel,
            user=self.user1,
            content="Parent comment"
        )

    @patch("interactions.views.public.comment_view.send_notification_to_user")
    def test_create_notification_and_send(self, mock_send):
        reply_comment = Comment.objects.create(
            novel=self.novel,
            user=self.user2,
            content="Reply comment",
            parent_comment=self.parent_comment
        )

        notify_user_reply_comment(reply_comment)

        mock_send.assert_called_once()

    def test_no_notification_if_no_parent(self):
        comment = Comment.objects.create(
            novel=self.novel,
            user=self.user2,
            content="No parent"
        )

        notify_user_reply_comment(comment)

    def test_no_notification_if_self_reply(self):
        reply_comment = Comment.objects.create(
            novel=self.novel,
            user=self.user1,
            content="Self reply",
            parent_comment=self.parent_comment
        )
        notify_user_reply_comment(reply_comment)
