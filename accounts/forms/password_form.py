from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from constants import (
    MIN_PASSWORD_LENGTH,
)

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label=_('Mật khẩu hiện tại'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu hiện tại')
        })
    )
    new_password = forms.CharField(
        label=_('Mật khẩu mới'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu mới')
        }),
        min_length=MIN_PASSWORD_LENGTH,
        help_text=_(f'Mật khẩu phải có ít nhất 8 ký tự')
    )
    confirm_password = forms.CharField(
        label=_('Xác nhận mật khẩu mới'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập lại mật khẩu mới')
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError(_('Mật khẩu hiện tại không đúng.'))
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError(_('Mật khẩu mới không khớp.'))
        
        return cleaned_data
