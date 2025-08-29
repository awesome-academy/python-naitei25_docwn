from typing import List
from django.contrib.contenttypes.models import ContentType
from interactions.models import Notification, Comment
from constants import (
    NotificationTypeChoices
)
from novels.models.chapter import Chapter
from novels.models.novel import Novel
from django.urls import reverse

class NotificationService:
    @staticmethod
    def get_user_notifications(user, limit: int, offset: int) -> List[Notification]:
        return Notification.objects.filter(user=user).order_by('-created_at')[offset:offset + limit]
    
    @staticmethod
    def create_notification(
        user,
        title: str,
        content: str,
        notification_type: str,
        related_object=None,
    ) -> Notification:
        """Tạo thông báo mới"""
        notification_data = {
            'user': user,
            'title': title,
            'content': content,
            'type': notification_type,
        }
        
        if related_object:
            notification_data.update({
                'content_type': ContentType.objects.get_for_model(related_object),
                'object_id': related_object.pk
            })
        
        return Notification.objects.create(**notification_data)

    @staticmethod
    def attach_link(notification):
        obj = getattr(notification, 'related_object', None)

        if obj:
            if isinstance(obj, Novel):
                return reverse("novels:novel_detail", kwargs={"novel_slug": obj.slug})
            if isinstance(obj, Chapter):
                return reverse(
                    "novels:chapter_detail",
                    kwargs={
                        "novel_slug": obj.volume.novel.slug, 
                        "chapter_slug": obj.slug,
                    }
                )
            if isinstance(obj, Comment):
                novel = obj.novel
                parent_id = obj.parent_comment_id if obj.parent_comment_id else obj.id
                link = reverse("novels:novel_detail", kwargs={"novel_slug": novel.slug})
                return f"{link}#comment-{parent_id}"
        return "#"
