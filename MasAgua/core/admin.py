from django.contrib import admin
from .models import Carrito, ItemCarrito, Orden, Pedido, Producto,Plan,Contrato, ProductoAdmin, UserProfile

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'direccion', 'estado', 'fecha_entrega', 'precio_total')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('cliente', 'direccion')


admin.site.register(Producto,ProductoAdmin)
admin.site.register(Plan)
admin.site.register(UserProfile)
admin.site.register(Contrato)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Orden)
