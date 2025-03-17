from django import forms
from django.utils import timezone
from finanzas.models.transaccion import Transaccion
from finanzas.models.categoria import Categoria

class TransaccionForm(forms.ModelForm):
    """
    Formulario para crear y editar transacciones financieras
    """
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
        """
        Personaliza el formulario basado en el usuario actual
        """
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        # Solo mostrar categorías del usuario actual
        if self.usuario:
            # Filtrar categorías según el tipo seleccionado
            if self.data.get('tipo'):
                tipo = self.data.get('tipo')
                self.fields['categoria'].queryset = Categoria.objects.filter(
                    usuario=self.usuario,
                    tipo=tipo
                )
            else:
                # Si es una edición, usar el tipo existente
                instance = kwargs.get('instance')
                if instance and instance.tipo:
                    self.fields['categoria'].queryset = Categoria.objects.filter(
                        usuario=self.usuario,
                        tipo=instance.tipo
                    )
                else:
                    # Por defecto, mostrar todas las categorías del usuario
                    self.fields['categoria'].queryset = Categoria.objects.filter(
                        usuario=self.usuario
                    )
                
        # Configura la fecha por defecto al momento actual
        self.fields['fecha'].initial = timezone.now()
    
    def clean_monto(self):
        """Valida que el monto sea positivo"""
        monto = self.cleaned_data.get('monto')
        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero")
        return monto
    
    def clean(self):
        """Validaciones adicionales que dependen de múltiples campos"""
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        categoria = cleaned_data.get('categoria')
        
        # Validar que la categoría coincida con el tipo de transacción
        if tipo and categoria and tipo != categoria.tipo:
            self.add_error('categoria', 
                f"La categoría seleccionada es de tipo '{categoria.get_tipo_display()}', debe coincidir con el tipo de transacción: '{dict(Transaccion.TIPO_CHOICES).get(tipo)}'")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Asigna el usuario a la transacción si no está definido"""
        transaccion = super().save(commit=False)
        
        if self.usuario and not transaccion.usuario_id:
            transaccion.usuario = self.usuario
            
        if commit:
            transaccion.save()
        
        return transaccion