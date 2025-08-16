from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from constants import (
    MAX_USERNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_ROLE_LENGTH,
    UserRole,
    MAX_TOKEN_LENGTH
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email là bắt buộc'))
        if not username:
            raise ValueError(_('Username là bắt buộc'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.WEBSITE_ADMIN.value)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser phải có is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser phải có is_superuser=True.'))
        
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, unique=True, verbose_name=_("Tên đăng nhập"))
    email = models.EmailField(max_length=MAX_EMAIL_LENGTH, unique=True, verbose_name=_("Email"))
    is_blocked = models.BooleanField(default=False, verbose_name=_("Bị khóa"))
    role = models.CharField(
        max_length=MAX_ROLE_LENGTH, 
        choices=UserRole.choices(),
        default=UserRole.USER.value,
        verbose_name=_("Vai trò")
    )
    
    is_active = models.BooleanField(default=True, verbose_name=_("Hoạt động"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Là nhân viên"))
    date_joined = models.DateTimeField(default=timezone.now, verbose_name=_("Ngày tham gia"))
    
    is_email_verified = models.BooleanField(default=False, verbose_name=_("Đã xác thực email"))
    email_verification_token = models.CharField(max_length=MAX_TOKEN_LENGTH, blank=True, null=True)
    
    password_reset_token = models.CharField(max_length=MAX_TOKEN_LENGTH, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('Người dùng')
        verbose_name_plural = _('Người dùng')
    
    def __str__(self):
        return self.email
    
    def get_name(self):
        if hasattr(self, 'profile') and self.profile.display_name:
            return self.profile.display_name
        return self.username
    
    def can_login(self):
        return self.is_active and not self.is_blocked
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_role = None
        
        if not is_new:
            try:
                old_instance = User.objects.get(pk=self.pk)
                old_role = old_instance.role
            except User.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Tự động gán group theo role
        if is_new or (old_role and old_role != self.role):
            self.assign_group_by_role()
            
    def assign_group_by_role(self):
        self.groups.clear()
        
        if self.role == UserRole.WEBSITE_ADMIN.value:
            group, created = Group.objects.get_or_create(name='Website Admins')
            self.groups.add(group)
        elif self.role == UserRole.USER.value:
            group, created = Group.objects.get_or_create(name='Regular Users')
            self.groups.add(group)
        elif self.role == UserRole.SYSTEM_ADMIN.value:
            group, created = Group.objects.get_or_create(name='System Admins')
            self.groups.add(group)
    
    def is_in_group(self, group_name):
        return self.groups.filter(name=group_name).exists()
    
    def is_website_admin(self):
        return (self.role == UserRole.WEBSITE_ADMIN.value or 
                self.is_in_group('Website Admins'))
    
    def is_moderator(self):
        return self.is_in_group('Moderators')
    
    def is_editor(self):
        return self.is_in_group('Editors')

@receiver(post_save, sender=User)
def ensure_user_group(sender, instance, created, **kwargs):
    if created:
        instance.assign_group_by_role()
