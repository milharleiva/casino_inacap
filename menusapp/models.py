from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario.username

class Administrador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario.username

class Menu(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.IntegerField() 

    def __str__(self):
        return self.nombre
    
class Boleta(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boletas')
    menu = models.ForeignKey(Menu, on_delete=models.SET_NULL, null=True, blank=True, related_name='boletas')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    codigo_autorizacion = models.CharField(max_length=64, blank=True, null=True)  # Código de autorización de Transbank
    token_transbank = models.CharField(max_length=64, blank=True, null=True)   # Asumiendo que deseas tener centavos
    
    # Puedes añadir otros campos que puedan ser necesarios para tu lógica de negocio,
    # como un campo de referencia para un sistema de pago externo, etc.

    def __str__(self):
        return f"Boleta {self.id} - Usuario: {self.usuario.username} - Estado: {self.estado}"
    


class Carrito(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.cantidad}x {self.menu.nombre} en el carrito de {self.carrito.usuario.username}"

    def get_cost(self):
        return self.menu.precio * self.cantidad
