from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserProfileForm, UserInfoForm
from accounts.models import User, UserProfile
from django.contrib import messages


@login_required(login_url='login')
def custProfile(request):
    user = request.user
    profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        user_form = UserInfoForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully !')
            return redirect('custprofile')   
        else:
            pass

    else:
        user_form = UserInfoForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    context={
        'user_form': user_form,
        'profile_form':profile_form,
        'profile': profile,
    }
    return render(request, 'customers/customer_profile.html', context)
