from django import forms
from django.contrib.auth.models import User
from finanzas.models.transferencia import Transferencia

class TransferenciaForm(forms.ModelForm):
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
        
    def clean_receptor_username(self):
        """Validar que el usuario receptor exista y no sea el mismo que el emisor"""
        username = self.cleaned_data['receptor_username']
        
        # Verificar que el usuario exista
        try:
            receptor = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('Este usuario no existe en el sistema.')
        
        # Verificar que no sea el usuario actual
        if self.instance and hasattr(self.instance, 'emisor') and self.instance.emisor == receptor:
            raise forms.ValidationError('No puedes transferir dinero a ti mismo.')
            
        return username
    
    def clean_monto(self):
        """Validar que el monto sea positivo y no exceda el máximo permitido"""
        monto = self.cleaned_data['monto']
        
        if monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor que cero.')
            
        # Puedes agregar una validación de límite máximo si lo necesitas
        if monto > 10000:  # Por ejemplo, un límite de 10,000
            raise forms.ValidationError('No puedes transferir más de 10,000 en una sola operación.')
            
        return monto
        
    def save(self, commit=True):
        """Sobrescribir el método save para asignar el receptor desde el username"""
        transferencia = super().save(commit=False)
        
        # Asignar el usuario receptor
        username = self.cleaned_data['receptor_username']
        transferencia.receptor = User.objects.get(username=username)
        
        if commit:
            transferencia.save()
            
        return transferencia
