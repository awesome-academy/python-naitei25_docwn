from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from .user import User

from constants import (
    MAX_NAME_LENGTH,
    MAX_GENDER_LENGTH,
    Gender,
)

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.RESTRICT, 
        related_name='profile',
        verbose_name=_("Người dùng")
    )
    display_name = models.CharField(
        max_length=MAX_NAME_LENGTH, 
        null=True, 
        blank=True,
        help_text=_("Tên hiển thị của người dùng"),
        verbose_name=_("Tên hiển thị")
    )
    gender = models.CharField(
        max_length=MAX_GENDER_LENGTH,
        choices=Gender.choices(),
        null=True,
        blank=True,
        verbose_name=_("Giới tính")
    )
    birthday = models.DateField(null=True, blank=True, verbose_name=_("Ngày sinh"))
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True, 
        blank=True,
        help_text=_("Ảnh đại diện của người dùng"),
        verbose_name=_("Ảnh đại diện")
    )
    description = models.TextField(
        null=True, 
        blank=True,
        help_text=_("Mô tả về bản thân"),
        verbose_name=_("Mô tả")
    )
    interest = models.TextField(
        null=True, 
        blank=True,
        help_text=_("Sở thích, thể loại truyện yêu thích"),
        verbose_name=_("Sở thích")
    )
    is_locked = models.BooleanField(
        default=False,
        help_text=_("Khóa profile"),
        verbose_name=_("Bị khóa")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Tạo lúc"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Cập nhật lúc"))
    
    class Meta:
        verbose_name = _('Hồ sơ người dùng')
        verbose_name_plural = _('Hồ sơ người dùng')
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    def get_name(self):
        return self.display_name or self.user.username
    
    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return '/static/images/default-avatar.png'
    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
