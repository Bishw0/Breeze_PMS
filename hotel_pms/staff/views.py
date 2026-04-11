from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import StaffProfile
from .forms import LoginForm, StaffProfileForm, UserCreateForm


def staff_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect(request.GET.get('next', 'dashboard'))
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'staff/login.html', {'form': form})


@login_required
def staff_logout(request):
    logout(request)
    return redirect('staff_login')


@login_required
def staff_list(request):
    profiles = StaffProfile.objects.select_related('user').filter(is_active=True)
    return render(request, 'staff/staff_list.html', {'profiles': profiles})


@login_required
def staff_create(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        profile_form = StaffProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, f'Staff member {user.get_full_name()} created.')
            return redirect('staff_list')
    else:
        user_form = UserCreateForm()
        profile_form = StaffProfileForm()
    return render(request, 'staff/staff_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Add Staff Member',
    })


@login_required
def my_profile(request):
    try:
        profile = request.user.staff_profile
    except StaffProfile.DoesNotExist:
        profile = None
    return render(request, 'staff/my_profile.html', {'profile': profile})
