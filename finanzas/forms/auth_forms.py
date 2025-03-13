from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from ..models import PerfilUsuario

class RegisterForm(UserCreationForm):
    """Formulario personalizado para registro de usuarios"""
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text=_('Requerido. Introduce una dirección de correo válida.')
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        help_text=_('Requerido. Introduce tu nombre.')
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        help_text=_('Requerido. Introduce tus apellidos.')
    )
    moneda_preferida = forms.ChoiceField(
        choices=PerfilUsuario.MONEDAS,
        required=True,
        help_text=_('Selecciona tu moneda preferida para mostrar los importes.')
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'moneda_preferida')
    
    def save(self, commit=True):
        """Guarda el usuario y actualiza su perfil con la moneda preferida"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Obtener o crear perfil de usuario
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)
            perfil.moneda_preferida = self.cleaned_data['moneda_preferida']
            perfil.save()
            
        return user 