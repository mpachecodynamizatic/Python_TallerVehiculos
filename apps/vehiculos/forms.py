from django import forms
from .models import Vehiculo


class VehiculoForm(forms.ModelForm):
    """
    Formulario para crear y editar vehículos.
    Incluye validaciones personalizadas y widgets con Tailwind CSS.
    """

    class Meta:
        model = Vehiculo
        fields = [
            'cliente', 'marca', 'modelo', 'anio', 'matricula', 'bastidor',
            'color', 'tipo_combustible', 'kilometraje', 'foto_vehiculo',
            'notas', 'activo'
        ]

        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Toyota, Ford, BMW...'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Corolla, Focus, Serie 3...'
            }),
            'anio': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '2020',
                'min': '1900',
                'max': '2100'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '1234ABC o M-1234-AB',
                'maxlength': '20'
            }),
            'bastidor': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Número VIN (17 caracteres)',
                'maxlength': '17'
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Blanco, Negro, Rojo...'
            }),
            'tipo_combustible': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'kilometraje': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '50000',
                'min': '0'
            }),
            'foto_vehiculo': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Información adicional sobre el vehículo...',
                'rows': 4
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
        }

    def clean_matricula(self):
        """Validación adicional de la matrícula"""
        matricula = self.cleaned_data.get('matricula', '').upper().strip()

        # Verificar duplicados (excepto el propio registro en edición)
        queryset = Vehiculo.objects.filter(matricula=matricula)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Ya existe un vehículo con esta matrícula.')

        return matricula

    def clean_bastidor(self):
        """Validación adicional del bastidor (VIN)"""
        bastidor = self.cleaned_data.get('bastidor', '').upper().strip()

        if bastidor:
            # Verificar longitud (VIN debe tener 17 caracteres)
            if len(bastidor) != 17:
                raise forms.ValidationError('El número de bastidor (VIN) debe tener exactamente 17 caracteres.')

            # Verificar duplicados (excepto el propio registro en edición)
            queryset = Vehiculo.objects.filter(bastidor=bastidor)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError('Ya existe un vehículo con este número de bastidor.')

        return bastidor

    def clean_anio(self):
        """Validación del año"""
        anio = self.cleaned_data.get('anio')

        if anio:
            from datetime import datetime
            anio_actual = datetime.now().year

            if anio < 1900:
                raise forms.ValidationError('El año debe ser mayor a 1900.')

            if anio > anio_actual + 1:
                raise forms.ValidationError(f'El año no puede ser mayor a {anio_actual + 1}.')

        return anio
