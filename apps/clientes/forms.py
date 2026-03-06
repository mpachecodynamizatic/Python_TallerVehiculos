from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    """
    Formulario para crear y editar clientes.
    Incluye validaciones personalizadas y widgets con Tailwind CSS.
    """

    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellidos', 'dni', 'email', 'telefono',
            'telefono_alternativo', 'direccion', 'ciudad',
            'codigo_postal', 'notas', 'activo'
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Juan'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'García López'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '12345678A',
                'maxlength': '10'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'cliente@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '+34600000000'
            }),
            'telefono_alternativo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '+34600000000 (opcional)'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Calle Principal 123'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Madrid'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '28001',
                'maxlength': '5'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Información adicional sobre el cliente...',
                'rows': 4
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
        }

    def clean_dni(self):
        """Validación adicional del DNI"""
        dni = self.cleaned_data.get('dni', '').upper()

        # Verificar duplicados (excepto el propio registro en edición)
        queryset = Cliente.objects.filter(dni=dni)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Ya existe un cliente con este DNI.')

        return dni

    def clean_telefono(self):
        """Validación del teléfono"""
        telefono = self.cleaned_data.get('telefono', '')
        # Limpiar espacios y guiones
        return telefono.replace(' ', '').replace('-', '')

    def clean_telefono_alternativo(self):
        """Validación del teléfono alternativo"""
        telefono = self.cleaned_data.get('telefono_alternativo', '')
        if telefono:
            return telefono.replace(' ', '').replace('-', '')
        return telefono
