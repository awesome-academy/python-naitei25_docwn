from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from accounts.forms import ProfileUpdateForm
from accounts.services import ProfileService


@login_required
def profile_view(request):
    user = request.user
    profile = ProfileService.get_user_profile(user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        result = ProfileService.update_profile(request, form, profile)
        
        if result['success']:
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile': profile,
        'form': form,
    })
