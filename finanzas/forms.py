from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from finanzas.models import PerfilUsuario, Transaccion, Transferencia, Categoria


# ── Auth Forms ──────────────────────────────────────────────────────────────

class RegisterForm(UserCreationForm):
    """Formulario personalizado para registro de usuarios."""
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
        """Guarda el usuario y actualiza su perfil con la moneda preferida."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)
            perfil.moneda_preferida = self.cleaned_data['moneda_preferida']
            perfil.save()

        return user


# ── Transaccion Form ────────────────────────────────────────────────────────

class TransaccionForm(forms.ModelForm):
    """Formulario para crear y editar transacciones financieras."""

    class Meta:
        model = Transaccion
        fields = ['fecha', 'monto', 'tipo', 'categoria', 'descripcion', 'comprobante']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descripción de la transacción',
                'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
            }),
            'monto': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01',
                'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
            }),
            'tipo': forms.Select(attrs={
                'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
            }),
            'categoria': forms.Select(attrs={
                'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
            }),
            'comprobante': forms.ClearableFileInput(attrs={
                'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
            }),
        }

    def __init__(self, *args, **kwargs):
        """Personaliza el formulario basado en el usuario actual."""
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if self.usuario:
            if self.data.get('tipo'):
                tipo = self.data.get('tipo')
                self.fields['categoria'].queryset = Categoria.objects.filter(
                    usuario=self.usuario,
                    tipo=tipo
                )
            else:
                instance = kwargs.get('instance')
                if instance and instance.tipo:
                    self.fields['categoria'].queryset = Categoria.objects.filter(
                        usuario=self.usuario,
                        tipo=instance.tipo
                    )
                else:
                    self.fields['categoria'].queryset = Categoria.objects.filter(
                        usuario=self.usuario
                    )

        self.fields['fecha'].initial = timezone.now()

    def clean_monto(self):
        """Valida que el monto sea positivo."""
        monto = self.cleaned_data.get('monto')
        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero")
        return monto

    def clean(self):
        """Validaciones adicionales que dependen de múltiples campos."""
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        categoria = cleaned_data.get('categoria')

        if tipo and categoria and tipo != categoria.tipo:
            self.add_error('categoria',
                f"La categoría seleccionada es de tipo '{categoria.get_tipo_display()}', "
                f"debe coincidir con el tipo de transacción: '{dict(Transaccion.TIPO_CHOICES).get(tipo)}'")

        return cleaned_data

    def save(self, commit=True):
        """Asigna el usuario a la transacción si no está definido."""
        transaccion = super().save(commit=False)

        if self.usuario and not transaccion.usuario_id:
            transaccion.usuario = self.usuario

        if commit:
            transaccion.save()

        return transaccion


# ── Transferencia Form ──────────────────────────────────────────────────────

class TransferenciaForm(forms.ModelForm):
    """Formulario para crear transferencias entre usuarios."""
    receptor_username = forms.CharField(
        label="Usuario destinatario",
        max_length=150,
        help_text="Ingresa el nombre de usuario del destinatario",
        widget=forms.TextInput(attrs={
            'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
        })
    )

    class Meta:
        model = Transferencia
        fields = ['receptor_username', 'monto', 'concepto']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01',
                'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
            }),
            'concepto': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Motivo de la transferencia',
                'style': 'background-color: #2D2D3A; color: #E2E2E2; border-color: #3F3F50;'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.emisor = kwargs.pop('emisor', None)
        super().__init__(*args, **kwargs)

    def clean_receptor_username(self):
        """Validar que el usuario receptor exista y no sea el mismo que el emisor."""
        username = self.cleaned_data['receptor_username']

        try:
            receptor = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('Este usuario no existe en el sistema.')

        emisor = self.emisor or getattr(self.instance, 'emisor', None)
        if emisor and emisor == receptor:
            raise forms.ValidationError('No puedes transferir dinero a ti mismo.')

        return username

    def clean_monto(self):
        """Validar que el monto sea positivo y no exceda el máximo permitido."""
        monto = self.cleaned_data['monto']

        if monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor que cero.')

        if monto > 10000:
            raise forms.ValidationError('No puedes transferir más de 10,000 en una sola operación.')

        return monto

    def save(self, commit=True):
        """Sobrescribir el método save para asignar el receptor desde el username."""
        transferencia = super().save(commit=False)

        username = self.cleaned_data['receptor_username']
        transferencia.receptor = User.objects.get(username=username)

        if commit:
            transferencia.save()

        return transferencia
