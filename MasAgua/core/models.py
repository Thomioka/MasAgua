from django.db import models

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
