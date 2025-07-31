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
    imagen = models.ImageField(upload_to='objetos/', null=True, blank=True)


class Accion(models.Model):
    tipo = [
        ('crear_cajon', 'Crear Cajón'),
        ('agregar_objeto', 'Agregar Objeto'),
        ('eliminar_objeto', 'Eliminar Objeto'),
        ('modificar_cajon', 'Modificar Cajón'),
        ('modificar_objeto', 'Modificar Objeto'),
    ]

    cajon = models.ForeignKey(Cajon, on_delete=models.CASCADE, related_name='acciones', null=True, blank=True)
    objetosAfectados = models.ManyToManyField(Objeto, related_name='acciones', blank=True)
    tipo = models.CharField(max_length=50, choices=tipo)
    descripcion = models.TextField(blank=True, null=True)  # Descripción detallada de la acción
    fecha_hora = models.DateTimeField(auto_now_add=True)  # Timestamp automático
    
    class Meta:
        ordering = ['-fecha_hora']  # Ordenar por fecha más reciente primero
        verbose_name = 'Acción'
        verbose_name_plural = 'Acciones'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
