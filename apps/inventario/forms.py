from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import CategoriaRepuesto, Repuesto, MovimientoInventario


class CategoriaRepuestoForm(forms.ModelForm):
    """
    Formulario para gestionar categorías de repuestos.
    """

    class Meta:
        model = CategoriaRepuesto
        fields = ['nombre', 'codigo', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre de la categoría...'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Código único...'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Descripción de la categoría...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].label = 'Nombre'
        self.fields['codigo'].label = 'Código'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['descripcion'].required = False
        self.fields['activo'].label = 'Categoría Activa'


class RepuestoForm(forms.ModelForm):
    """
    Formulario para gestionar repuestos.
    """

    class Meta:
        model = Repuesto
        fields = [
            'codigo', 'nombre', 'descripcion', 'categoria', 'marca',
            'ubicacion_almacen', 'stock_actual', 'stock_minimo', 'stock_maximo',
            'precio_compra', 'precio_venta', 'iva', 'activo', 'foto'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Código único...'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre del repuesto...'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'ubicacion_almacen': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ej: Estante A3'
            }),
            'stock_actual': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'stock_maximo': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'iva': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar solo categorías activas
        self.fields['categoria'].queryset = CategoriaRepuesto.objects.filter(activo=True)

        # Campos opcionales
        self.fields['descripcion'].required = False
        self.fields['marca'].required = False
        self.fields['ubicacion_almacen'].required = False
        self.fields['stock_maximo'].required = False
        self.fields['foto'].required = False

        # Labels
        self.fields['codigo'].label = 'Código'
        self.fields['nombre'].label = 'Nombre'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['categoria'].label = 'Categoría'
        self.fields['marca'].label = 'Marca'
        self.fields['ubicacion_almacen'].label = 'Ubicación en Almacén'
        self.fields['stock_actual'].label = 'Stock Actual'
        self.fields['stock_minimo'].label = 'Stock Mínimo'
        self.fields['stock_maximo'].label = 'Stock Máximo'
        self.fields['precio_compra'].label = 'Precio de Compra (€)'
        self.fields['precio_venta'].label = 'Precio de Venta (€)'
        self.fields['iva'].label = 'IVA (%)'
        self.fields['activo'].label = 'Repuesto Activo'
        self.fields['foto'].label = 'Foto del Repuesto'

        # Valores por defecto
        if not self.instance.pk:
            self.fields['stock_actual'].initial = Decimal('0.00')
            self.fields['stock_minimo'].initial = Decimal('5.00')
            self.fields['iva'].initial = Decimal('21.00')


class AjusteStockForm(forms.Form):
    """
    Formulario para realizar ajustes de stock.
    """
    tipo_movimiento = forms.ChoiceField(
        choices=MovimientoInventario.TipoMovimiento.choices,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        }),
        label='Tipo de Movimiento'
    )

    cantidad = forms.DecimalField(
        min_value=Decimal('0.01'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        label='Cantidad'
    )

    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Notas sobre el movimiento (opcional)...'
        }),
        label='Notas'
    )

    def __init__(self, *args, **kwargs):
        self.repuesto = kwargs.pop('repuesto', None)
        super().__init__(*args, **kwargs)

    def clean_cantidad(self):
        """Validar que la cantidad no deje el stock negativo"""
        cantidad = self.cleaned_data.get('cantidad')
        tipo = self.cleaned_data.get('tipo_movimiento')

        if self.repuesto and tipo == MovimientoInventario.TipoMovimiento.SALIDA:
            if cantidad > self.repuesto.stock_actual:
                raise ValidationError(
                    f'No hay suficiente stock. Stock actual: {self.repuesto.stock_actual}'
                )

        return cantidad
