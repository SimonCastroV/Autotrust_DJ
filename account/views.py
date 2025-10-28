from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from vehicles.models import Vehicle
from .forms import UserForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('vehicle_list')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('vehicle_list')
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'account/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def profile_view(request):
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')

    mis_vehiculos = Vehicle.objects.filter(usuario=request.user)
    favoritos = request.user.vehiculos_favoritos.all()

    return render(request, 'account/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'mis_vehiculos': mis_vehiculos,
        'favoritos': favoritos,
    })
