from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
                messages.success(request, f"Bienvenido, {username}!")
                return redirect('finanzas:dashboard')
            else:
                messages.error(request, "Nombre de usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'finanzas/login.html', {'form': form})

def register_view(request):
    """Vista para registrarse"""
    if request.user.is_authenticated:
        return redirect('finanzas:dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Cuenta creada exitosamente!")
            return redirect('finanzas:dashboard')
        else:
            messages.error(request, "Error al crear la cuenta. Por favor revisa los datos.")
    else:
        form = UserCreationForm()
        
    return render(request, 'finanzas/register.html', {'form': form})

@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('finanzas:login')
