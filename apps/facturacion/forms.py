from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from decimal import Decimal

from .models import Factura, LineaFactura
from apps.clientes.models import Cliente


class FacturaForm(forms.ModelForm):
    """
    Formulario para gestionar facturas.
    """

    class Meta:
        model = Factura
        fields = [
            'cliente', 'orden_trabajo', 'fecha_emision', 'fecha_vencimiento',
            'estado', 'metodo_pago', 'notas'
        ]
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'orden_trabajo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'fecha_emision': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Notas adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar solo clientes activos
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)

        # Campos opcionales
        self.fields['orden_trabajo'].required = False
        self.fields['metodo_pago'].required = False
        self.fields['notas'].required = False

        # Labels
        self.fields['cliente'].label = 'Cliente'
        self.fields['orden_trabajo'].label = 'Orden de Trabajo (opcional)'
        self.fields['fecha_emision'].label = 'Fecha de Emisión'
        self.fields['fecha_vencimiento'].label = 'Fecha de Vencimiento'
        self.fields['estado'].label = 'Estado'
        self.fields['metodo_pago'].label = 'Método de Pago'
        self.fields['notas'].label = 'Notas'


class LineaFacturaForm(forms.ModelForm):
    """
    Formulario para líneas de factura.
    """

    class Meta:
        model = LineaFactura
        fields = ['descripcion', 'cantidad', 'precio_unitario', 'descuento', 'iva']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Descripción del concepto...'
            }),
            'cantidad': forms.NumberInput(attrs={
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
            'iva': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Labels
        self.fields['descripcion'].label = 'Descripción'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['precio_unitario'].label = 'Precio €'
        self.fields['descuento'].label = 'Desc. %'
        self.fields['iva'].label = 'IVA %'

        # Valores por defecto
        if not self.instance.pk:
            self.fields['descuento'].initial = Decimal('0.00')
            self.fields['iva'].initial = Decimal('21.00')


# Formset para líneas de factura
LineaFacturaFormSet = inlineformset_factory(
    Factura,
    LineaFactura,
    form=LineaFacturaForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class RegistrarPagoForm(forms.Form):
    """
    Formulario para registrar pagos en facturas.
    """
    monto = forms.DecimalField(
        min_value=Decimal('0.01'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        label='Monto a Pagar (€)'
    )

    metodo_pago = forms.ChoiceField(
        choices=Factura.MetodoPago.choices,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        }),
        label='Método de Pago'
    )

    fecha_pago = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        }),
        label='Fecha de Pago'
    )

    def __init__(self, *args, **kwargs):
        self.factura = kwargs.pop('factura', None)
        super().__init__(*args, **kwargs)

        if self.factura:
            self.fields['monto'].help_text = f'Saldo pendiente: €{self.factura.saldo_pendiente}'
            self.fields['monto'].initial = self.factura.saldo_pendiente

        # Fecha por defecto: hoy
        from django.utils import timezone
        self.fields['fecha_pago'].initial = timezone.now().date()

    def clean_monto(self):
        """Validar que el monto no exceda el saldo pendiente"""
        monto = self.cleaned_data.get('monto')

        if self.factura:
            if monto > self.factura.saldo_pendiente:
                raise ValidationError(
                    f'El monto excede el saldo pendiente (€{self.factura.saldo_pendiente})'
                )

        return monto
