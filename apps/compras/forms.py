from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from decimal import Decimal

from .models import Proveedor, OrdenCompra, LineaCompra
from apps.inventario.models import Repuesto


class ProveedorForm(forms.ModelForm):
    """
    Formulario para gestionar proveedores.
    """

    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'cif', 'email', 'telefono', 'direccion', 'ciudad',
            'codigo_postal', 'pais', 'contacto_principal', 'notas', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre o razón social...'
            }),
            'cif': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'CIF/NIF...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'email@proveedor.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': '+34 XXX XXX XXX'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Calle, número...'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ciudad'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': '28001'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'contacto_principal': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre del contacto...'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Notas adicionales...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Campos opcionales
        self.fields['contacto_principal'].required = False
        self.fields['notas'].required = False

        # Labels
        self.fields['nombre'].label = 'Nombre / Razón Social'
        self.fields['cif'].label = 'CIF/NIF'
        self.fields['email'].label = 'Email'
        self.fields['telefono'].label = 'Teléfono'
        self.fields['direccion'].label = 'Dirección'
        self.fields['ciudad'].label = 'Ciudad'
        self.fields['codigo_postal'].label = 'Código Postal'
        self.fields['pais'].label = 'País'
        self.fields['contacto_principal'].label = 'Contacto Principal'
        self.fields['notas'].label = 'Notas'
        self.fields['activo'].label = 'Proveedor Activo'


class OrdenCompraForm(forms.ModelForm):
    """
    Formulario para gestionar órdenes de compra.
    """

    class Meta:
        model = OrdenCompra
        fields = [
            'proveedor', 'fecha_orden', 'fecha_entrega_esperada', 'estado', 'notas'
        ]
        widgets = {
            'proveedor': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'fecha_orden': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'fecha_entrega_esperada': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Notas sobre la orden...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar solo proveedores activos
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)

        # Campos opcionales
        self.fields['fecha_entrega_esperada'].required = False
        self.fields['notas'].required = False

        # Labels
        self.fields['proveedor'].label = 'Proveedor'
        self.fields['fecha_orden'].label = 'Fecha de Orden'
        self.fields['fecha_entrega_esperada'].label = 'Fecha de Entrega Esperada'
        self.fields['estado'].label = 'Estado'
        self.fields['notas'].label = 'Notas'


class LineaCompraForm(forms.ModelForm):
    """
    Formulario para líneas de compra.
    """

    class Meta:
        model = LineaCompra
        fields = ['repuesto', 'cantidad_solicitada', 'precio_unitario', 'descuento']
        widgets = {
            'repuesto': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'cantidad_solicitada': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'descuento': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar solo repuestos activos
        self.fields['repuesto'].queryset = Repuesto.objects.filter(activo=True)

        # Labels
        self.fields['repuesto'].label = 'Repuesto'
        self.fields['cantidad_solicitada'].label = 'Cantidad'
        self.fields['precio_unitario'].label = 'Precio Unitario (€)'
        self.fields['descuento'].label = 'Descuento (%)'

        # Valores por defecto
        if not self.instance.pk:
            self.fields['descuento'].initial = Decimal('0.00')


# Formset para líneas de compra
LineaCompraFormSet = inlineformset_factory(
    OrdenCompra,
    LineaCompra,
    form=LineaCompraForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class RecibirMercanciaForm(forms.Form):
    """
    Formulario para recibir mercancía de una línea de compra.
    """
    cantidad = forms.DecimalField(
        min_value=Decimal('0.01'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        label='Cantidad a Recibir'
    )

    def __init__(self, *args, **kwargs):
        self.linea_compra = kwargs.pop('linea_compra', None)
        super().__init__(*args, **kwargs)

        if self.linea_compra:
            self.fields['cantidad'].help_text = (
                f'Pendiente: {self.linea_compra.cantidad_pendiente} unidades'
            )

    def clean_cantidad(self):
        """Validar que la cantidad no exceda lo pendiente"""
        cantidad = self.cleaned_data.get('cantidad')

        if self.linea_compra:
            if cantidad > self.linea_compra.cantidad_pendiente:
                raise ValidationError(
                    f'No se puede recibir más de lo pendiente. '
                    f'Pendiente: {self.linea_compra.cantidad_pendiente}'
                )

        return cantidad
