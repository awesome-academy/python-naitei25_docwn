from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from accounts.services import PasswordService


@login_required
def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        result = PasswordService.change_password(
            request, current_password, new_password, confirm_password
        )
        
        if result['success']:
            return redirect(result['redirect_url'])
    
    return render(request, 'accounts/change_password.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        result = PasswordService.initiate_password_reset(email)
        
        if result['success']:
            # Tại đây bạn có thể gửi email với reset_token
            reset_url = request.build_absolute_uri(f'/accounts/reset-password/{result["reset_token"]}/')
            # TODO: Implement email sending
            
            messages.success(request, result['message'])
            return redirect('accounts:login')
        else:
            messages.error(request, result['message'])
    
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, token):
    user = PasswordService.get_user_by_reset_token(token)
    
    if not user:
        messages.error(request, _('Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.'))
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        result = PasswordService.reset_password(user, new_password, confirm_password)
        
        if result['success']:
            messages.success(request, result['message'])
            return redirect('accounts:login')
        else:
            messages.error(request, result['message'])
    
    return render(request, 'accounts/reset_password.html', {'token': token})
