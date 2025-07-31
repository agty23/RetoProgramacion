from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cajon

# Create your views here.

def crear_caja(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.POST.get('nombre')
        capacidad_maxima = request.POST.get('capacidadMax')
        
        try:
            # Crear una nueva instancia de Cajon
            nuevo_cajon = Cajon(
                nombre=nombre,
                capacidadMaxima=int(capacidad_maxima)
            )
            # Guardar en la base de datos
            nuevo_cajon.save()
            
            # Mostrar mensaje de éxito
            messages.success(request, f'Caja "{nombre}" creada exitosamente!')
            
            # Redireccionar para evitar reenvío del formulario
            return redirect('crear_caja')
            
        except ValueError:
            # Error si la capacidad no es un número válido
            messages.error(request, 'La capacidad máxima debe ser un número válido.')
        except Exception as e:
            # Error general
            messages.error(request, f'Error al crear la caja: {str(e)}')
    
    # Si es GET o hubo error, mostrar el formulario
    # Obtener todas las cajas existentes para mostrarlas
    cajas = Cajon.objects.all()
    context = {
        'cajas': cajas
    }
    return render(request, 'InterfazCrearCajas.html', context)
