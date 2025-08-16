from django import forms
from django.utils.translation import gettext_lazy as _
from accounts.models import UserProfile
from constants import (
    MIN_TEXTAREA_ROWS
)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'display_name',
            'gender',
            'birthday',
            'avatar',
            'description',
            'interest',
            'is_locked',
        ]
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': MIN_TEXTAREA_ROWS}),
            'interest': forms.Textarea(attrs={'rows': MIN_TEXTAREA_ROWS}),
        }
        labels = {
            'display_name': _('Tên hiển thị'),
            'gender': _('Giới tính'),
            'birthday': _('Ngày sinh'),
            'avatar': _('Ảnh đại diện'),
            'description': _('Mô tả bản thân'),
            'interest': _('Sở thích'),
            'is_locked': _('Ẩn hồ sơ'),
        }
