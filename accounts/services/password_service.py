from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from datetime import timedelta
import uuid

from accounts.models import User
from accounts.utils import validate_password


class PasswordService:
    @staticmethod
    def change_password(request, current_password, new_password, confirm_password):
        user = request.user
        
        # Validate current password
        if not user.check_password(current_password):
            return {
                'success': False,
                'message': _('Mật khẩu hiện tại không đúng.')
            }
        
        # Validate new password
        validation_result = validate_password(new_password, confirm_password)
        if not validation_result['valid']:
            return {
                'success': False,
                'message': validation_result['message']
            }
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        messages.success(request, _('Đổi mật khẩu thành công!'))
        
        return {
            'success': True,
            'message': _('Đổi mật khẩu thành công!'),
            'redirect_url': 'accounts:login'
        }
    
    @staticmethod
    def initiate_password_reset(email):
        try:
            user = User.objects.get(email=email)
            reset_token = str(uuid.uuid4())
            user.password_reset_token = reset_token
            user.password_reset_expires = timezone.now() + timedelta(hours=1)
            user.save()
            
            return {
                'success': True,
                'message': _('Liên kết đặt lại mật khẩu đã được gửi đến email của bạn.'),
                'reset_token': reset_token
            }
        except User.DoesNotExist:
            return {
                'success': False,
                'message': _('Email không tồn tại trong hệ thống.')
            }
    
    @staticmethod
    def get_user_by_reset_token(token):
        try:
            return User.objects.get(
                password_reset_token=token,
                password_reset_expires__gt=timezone.now()
            )
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def reset_password(user, new_password, confirm_password):
        validation_result = validate_password(new_password, confirm_password)
        if not validation_result['valid']:
            return {
                'success': False,
                'message': validation_result['message']
            }
        
        # Reset password
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save()
        
        return {
            'success': True,
            'message': _('Đặt lại mật khẩu thành công!')
        }
