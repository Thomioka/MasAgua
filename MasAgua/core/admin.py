from django.contrib import admin
from .models import Pedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'direccion', 'estado', 'fecha_entrega', 'precio_total')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('cliente', 'direccion')
