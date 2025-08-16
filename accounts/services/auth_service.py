from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from accounts.utils import set_session_expiry


class AuthService:
    @staticmethod
    def authenticate_user(request, email, password, remember_me=False):
        user = authenticate(request, email=email, password=password)
        
        if user is None:
            return {
                'success': False,
                'message': _('Email hoặc mật khẩu không đúng.')
            }
        
        if not user.can_login():
            if user.is_blocked:
                message = _('Tài khoản của bạn đã bị khóa.')
            else:
                message = _('Tài khoản chưa được kích hoạt.')
            
            return {
                'success': False,
                'message': message
            }
        
        # Đăng nhập thành công
        login(request, user)
        set_session_expiry(request, remember_me)
        
        messages.success(request, _('Chào mừng %(username)s!') % {'username': user.get_name()})
        next_url = request.GET.get('next') or settings.LOGIN_REDIRECT_URL
        
        return {
            'success': True,
            'redirect_url': next_url,
            'message': _('Đăng nhập thành công!')
        }
    
    @staticmethod
    def logout_user(request):
        username = None
        if request.user.is_authenticated:
            username = request.user.get_name()
            logout(request)
            messages.success(request, _('Tạm biệt %(username)s!') % {'username': username})
        
        return request.GET.get('next') or settings.LOGOUT_REDIRECT_URL
    
    @staticmethod
    def register_user(form):
        return form.save()
