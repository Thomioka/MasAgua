from django.db import models

from django.contrib import admin

from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Pedido(models.Model):
    cliente = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    fecha_entrega = models.DateField()
    cantidad = models.IntegerField(default=1)  # NUEVO
    estado = models.CharField(max_length=50, default='pendiente')
    precio_total = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.precio_total = self.cantidad * 7000  # calcula automáticamente
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente} - {self.estado}"

class UserProfile(models.Model):

    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=settings.ROLES, default='cliente')
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Producto(models.Model):
    TIPO_PRODUCTO_CHOICES = [
        ('BIDON', 'Bidón de Agua'),
        ('DISPENSADOR', 'Dispensador'),
        ('ACCESORIO', 'Accesorio'),
    ]
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    tipo_producto = models.CharField(max_length=20, choices=TIPO_PRODUCTO_CHOICES)

    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_producto_display()}"
    
#administrar productos
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_producto', 'precio', 'stock', 'activo')
    list_filter = ('tipo_producto', 'activo')
    search_fields = ('nombre', 'descripcion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'precio', 'stock', 'activo')
        }),
        ('Tipos y Categorías', {
            'fields': ('tipo_producto',),
        }),
        ('Imagen', {
            'fields': ('imagen',),
            'classes': ('wide',)
        }),
    )

class Plan(models.Model):
    TIPO_PLAN_CHOICES = [
        ('MENSUAL', 'Plan Mensual'),
        ('TRIMESTRAL', 'Plan Trimestral'),
        ('ANUAL', 'Plan Anual'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_plan = models.CharField(max_length=15, choices=TIPO_PLAN_CHOICES)
    frecuencia_entrega = models.PositiveIntegerField(help_text="Cantidad de bidones por mes")
    incluye_dispensador = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='planes/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_plan_display()}"
    

class Contrato(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('PAUSADO', 'Pausado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    fecha_proxima_entrega = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ACTIVO')
    direccion_entrega = models.TextField()
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Contrato #{self.id} - {self.cliente}"
    
#CUANDO SE PAGA CON WEBPAY SE CREA UNA ORDEN
class Orden(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='pendiente')
    
    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"
#CARRITO DE COMPRAS
class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    confirmado = models.BooleanField(default=False)
    orden_relacionada = models.ForeignKey(Orden, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    def total(self):
        return sum(item.subtotal() for item in self.items.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
