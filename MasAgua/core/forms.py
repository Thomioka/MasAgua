from django import forms
from .models import Pedido, Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'fecha_creacion': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a cero")
        return precio

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['direccion', 'fecha_entrega', 'cantidad']
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
        }