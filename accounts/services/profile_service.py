from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class ProfileService:
    @staticmethod
    def get_user_profile(user):
        return getattr(user, 'profile', None)
    
    @staticmethod
    def update_profile(request, form, profile):
        if form.is_valid():
            form.save()
            messages.success(request, _('Cập nhật thông tin thành công!'))
            return {
                'success': True,
                'message': _('Cập nhật thông tin thành công!')
            }
        else:
            messages.error(request, _('Có lỗi xảy ra. Vui lòng kiểm tra lại.'))
            return {
                'success': False,
                'message': _('Có lỗi xảy ra. Vui lòng kiểm tra lại.')
            }
