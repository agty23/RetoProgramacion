from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cajon, Objeto, Accion

# Función auxiliar para registrar acciones
def registrar_accion(tipo_accion, cajon=None, objeto=None, descripcion=""):
    """
    Registra una acción en el sistema
    """
    try:
        accion = Accion(
            tipo=tipo_accion,
            cajon=cajon,
            descripcion=descripcion
        )
        accion.save()
        
        # Si hay un objeto involucrado, lo agregamos a la relación ManyToMany
        if objeto:
            accion.objetosAfectados.add(objeto)
            
        return accion
    except Exception as e:
        print(f"Error al registrar acción: {str(e)}")
        return None

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
            
            # Registrar la acción
            registrar_accion(
                tipo_accion='crear_cajon',
                cajon=nuevo_cajon,
                descripcion=f'Se creó la caja "{nombre}" con capacidad máxima de {capacidad_maxima} objetos'
            )
            
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
    # Obtener las últimas 5 acciones para mostrar en el dashboard
    ultimas_acciones = Accion.objects.all().order_by('-fecha_hora')[:5]
    
    context = {
        'cajas': cajas,
        'ultimas_acciones': ultimas_acciones,
    }
    return render(request, 'InterfazCrearCajas.html', context)

def añadir_objeto(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_objeto = request.POST.get('nombre')
        tipo_objeto = request.POST.get('tipoObjeto')
        tamanio_objeto = request.POST.get('tamanio', 'mediano')  # Valor por defecto
        caja_id = request.POST.get('caja')

        try:
            # Validar que todos los campos requeridos estén presentes
            if not nombre_objeto or not tipo_objeto or not caja_id:
                messages.error(request, 'Por favor, completa todos los campos requeridos.')
                raise ValueError('Campos incompletos')
            
            # Obtener la caja seleccionada
            caja = Cajon.objects.get(id=caja_id)
            
            # Validar el tipo de objeto (debe estar en las opciones válidas)
            tipos_validos = ['ropa', 'peleria', 'cables', 'herramientas', 'juguetes', 'papeleria', 'electronica']
            if tipo_objeto.lower() not in tipos_validos:
                # Si el tipo no está en la lista, usamos 'papeleria' como valor por defecto
                tipo_objeto = 'papeleria'
            
            # Crear el nuevo objeto
            nuevo_objeto = Objeto(
                nombre=nombre_objeto,
                tipo=tipo_objeto.lower(),
                tamanio=tamanio_objeto
            )
            nuevo_objeto.save()
            
            # Añadir el objeto a la caja
            caja.objetos.add(nuevo_objeto)
            caja.save()
            
            # Registrar la acción
            registrar_accion(
                tipo_accion='agregar_objeto',
                cajon=caja,
                objeto=nuevo_objeto,
                descripcion=f'Se agregó el objeto "{nombre_objeto}" (tipo: {tipo_objeto}, tamaño: {tamanio_objeto}) a la caja "{caja.nombre}"'
            )

            # Mostrar mensaje de éxito
            messages.success(request, f'Objeto "{nombre_objeto}" añadido a la caja "{caja.nombre}" exitosamente!')

            # Redireccionar para evitar reenvío del formulario
            return redirect('añadir_objeto')

        except Cajon.DoesNotExist:
            messages.error(request, 'La caja seleccionada no existe.')
        except Exception as e:
            messages.error(request, f'Error al añadir el objeto: {str(e)}')

    # Si es GET o hubo error, mostrar el formulario
    cajas = Cajon.objects.all()
    objetos = Objeto.objects.all()
    
    # Obtener las opciones de tipo y tamaño para el template
    tipos_objeto = [
        ('ropa', 'Ropa'),
        ('peleria', 'Pelería'),
        ('cables', 'Cables'),
        ('herramientas', 'Herramientas'),
        ('juguetes', 'Juguetes'),
        ('papeleria', 'Papelería'),
        ('electronica', 'Electrónica'),
    ]
    
    tamanios_objeto = [
        ('pequeno', 'Pequeño'),
        ('mediano', 'Mediano'),
        ('grande', 'Grande'),
    ]
    
    context = {
        'cajas': cajas,
        'objetos': objetos,
        'tipos_objeto': tipos_objeto,
        'tamanios_objeto': tamanios_objeto,
    }
    return render(request, 'InterfazAñadirObjetos.html', context)

def historial_acciones(request):
    """
    Vista para mostrar el historial de todas las acciones realizadas en el sistema
    """
    # Obtener todas las acciones ordenadas por fecha (más recientes primero)
    acciones = Accion.objects.all().order_by('-fecha_hora')
    
    # Paginación opcional (mostrar 20 acciones por página)
    from django.core.paginator import Paginator
    paginator = Paginator(acciones, 20)  # 20 acciones por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'acciones': page_obj,
        'total_acciones': acciones.count(),
    }
    return render(request, 'historial_acciones.html', context)