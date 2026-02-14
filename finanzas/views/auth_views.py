import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from finanzas.forms.auth_forms import RegisterForm

logger = logging.getLogger(__name__)


def login_view(request):
    """Vista para iniciar sesión"""
    if request.user.is_authenticated:
        return redirect('finanzas:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info("Login exitoso: user=%s", username)
                messages.success(request, f"Bienvenido, {username}!")
                return redirect('finanzas:dashboard')
            else:
                logger.warning("Login fallido (authenticate): user=%s", username)
                messages.error(request, "Nombre de usuario o contraseña incorrectos.")
        else:
            logger.warning("Login fallido (form inválido): ip=%s", request.META.get('REMOTE_ADDR'))
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()

    return render(request, 'finanzas/login.html', {'form': form})


def register_view(request):
    """Vista para registrarse"""
    if request.user.is_authenticated:
        return redirect('finanzas:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info("Nuevo usuario registrado: user=%s (id=%d)", user.username, user.id)
            messages.success(request, "¡Cuenta creada exitosamente!")
            return redirect('finanzas:dashboard')
        else:
            logger.warning("Registro fallido: errores=%s", form.errors)
            messages.error(request, "Error al crear la cuenta. Por favor revisa los datos.")
    else:
        form = RegisterForm()

    return render(request, 'finanzas/register.html', {'form': form})


@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    username = request.user.username
    logout(request)
    logger.info("Logout: user=%s", username)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('finanzas:login')
