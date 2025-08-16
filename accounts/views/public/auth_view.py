from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from accounts.forms import UserRegistrationForm, UserLoginForm
from accounts.services import AuthService


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = AuthService.register_user(form)
        messages.success(self.request, _('Đăng ký thành công! Vui lòng đăng nhập để tiếp tục.'))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, _('Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.'))
        return super().form_invalid(form)


@csrf_protect
@never_cache
def login_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next') or settings.LOGIN_REDIRECT_URL
        return redirect(next_url)
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            result = AuthService.authenticate_user(
                request, email, password, remember_me
            )
            
            if result['success']:
                return redirect(result['redirect_url'])
            else:
                messages.error(request, result['message'])
        else:
            messages.error(request, _('Thông tin đăng nhập không hợp lệ.'))
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    redirect_url = AuthService.logout_user(request)
    return redirect(redirect_url)
