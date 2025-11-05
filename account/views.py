from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileForm, UserForm
from vehicles.models import Vehicle
from chatt.models import Conversation
from django.contrib import messages  


# ------------------------------
# LOGIN
# ------------------------------
def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.user.is_authenticated:
        return redirect(next_url or 'catalogo')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(next_url or 'catalogo')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
        'next': next_url,
    }
    return render(request, 'account/login.html', context)


# ------------------------------
# REGISTER
# ------------------------------
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Guardar datos adicionales en el perfil
            profile = user.profile
            profile.telefono = form.cleaned_data.get('telefono')
            profile.ciudad = form.cleaned_data.get('ciudad_residencia')
            profile.save()

            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'account/register.html', {'form': form})


# ------------------------------
# LOGOUT
# ------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------------------
# PROFILE
# ------------------------------
@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, " Tus cambios se han guardado correctamente.")
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    mis_vehiculos = Vehicle.objects.filter(usuario=user)
    favoritos = user.vehiculos_favoritos.all()
    seller_conversations = (
        Conversation.objects.filter(seller=user)
        .select_related("vehicle", "buyer")
        .order_by("-created_at")
    )

    return render(request, 'account/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'mis_vehiculos': mis_vehiculos,
        'favoritos': favoritos,
        'seller_conversations': seller_conversations,
    })
