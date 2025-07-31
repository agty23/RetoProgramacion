from django.db import models

# Create your models here.
class Cajon(models.Model):
    nombre = models.CharField(max_length=100)
    capacidadMaxima = models.IntegerField()
    objetos = models.ManyToManyField('Objeto', related_name='cajones')

class Objeto(models.Model):
    tipo = [
        ('ropa', 'Ropa'),
        ('peleria', 'Peleria'),
        ('cables', 'Cables'),
        ('herramientas', 'Herramientas'),
        ('juguetes', 'Juguetes'),
        ('papeleria', 'Papeleria'),
        ('electronica', 'Electronica'),
    ]

    tamanio = [
        ('pequeno', 'Pequeño'),
        ('mediano', 'Mediano'),
        ('grande', 'Grande'),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=tipo)
    tamanio = models.CharField(max_length=50, choices=tamanio)

class Accion(models.Model):
    tipo = [
        ('agregar', 'Agregar'),
        ('eliminar', 'Eliminar'),
        ('modificar', 'Modificar'),
    ]

    cajon = models.ForeignKey(Cajon, on_delete=models.CASCADE, related_name='acciones')
    objetosAfectados = models.ManyToManyField(Objeto, related_name='acciones', blank=True)
    tipo = models.CharField(max_length=50, choices=tipo)

    
