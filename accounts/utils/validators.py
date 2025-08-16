from django.utils.translation import gettext_lazy as _
from constants import MIN_PASSWORD_LENGTH


def validate_password(new_password, confirm_password):
    if new_password != confirm_password:
        return {
            'valid': False,
            'message': _('Mật khẩu mới không khớp.')
        }
    
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return {
            'valid': False,
            'message': _('Mật khẩu phải có ít nhất 8 ký tự.')
        }
    
    return {
        'valid': True,
        'message': _('Mật khẩu hợp lệ.')
    }
