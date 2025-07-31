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


def crear_caja(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        capacidad_maxima = request.POST.get('capacidadMax')

        try:
            nuevo_cajon = Cajon(
                nombre=nombre,
                capacidadMaxima=int(capacidad_maxima)
            )
            nuevo_cajon.save()
            
            # Registrar la acción
            registrar_accion(
                tipo_accion='crear_cajon',
                cajon=nuevo_cajon,
                descripcion=f'Se creó la caja "{nombre}" con capacidad máxima de {capacidad_maxima} objetos'
            )
            
            # Mostrar mensaje de éxito
            messages.success(request, f'Caja "{nombre}" creada exitosamente!')

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
        foto = request.FILES.get('foto')

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
                tamanio=tamanio_objeto,
                imagen=foto
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

def detalle_caja(request, caja_id):
    """
    Vista para mostrar el detalle de una caja específica con opciones de ordenamiento
    """
    try:
        caja = Cajon.objects.get(id=caja_id)
    except Cajon.DoesNotExist:
        messages.error(request, 'La caja no existe.')
        return redirect('crear_caja')
    
    # Registrar la acción de visualizar caja
    registrar_accion(
        tipo_accion='visualizar_caja',
        cajon=caja,
        descripcion=f'Se visualizó y organizó el contenido de la caja "{caja.nombre}"'
    )
    
    # Obtener parámetro de ordenamiento
    orden = request.GET.get('orden', 'nombre')  # Por defecto ordenar por nombre
    
    # Ordenar objetos según el parámetro
    if orden == 'nombre':
        objetos = caja.objetos.all().order_by('nombre')
    elif orden == 'tipo':
        objetos = caja.objetos.all().order_by('tipo', 'nombre')
    elif orden == 'tamanio':
        # Ordenar por tamaño: pequeño, mediano, grande
        from django.db.models import Case, When, Value, IntegerField
        objetos = caja.objetos.all().annotate(
            orden_tamanio=Case(
                When(tamanio='pequeno', then=Value(1)),
                When(tamanio='mediano', then=Value(2)),
                When(tamanio='grande', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('orden_tamanio', 'nombre')
    else:
        objetos = caja.objetos.all().order_by('nombre')
    
    # Detectar duplicados (objetos con el mismo nombre, tipo y tamaño)
    duplicados = []
    objetos_revisados = {}
    
    for objeto in objetos:
        clave = f"{objeto.nombre.lower().strip()}_{objeto.tipo}_{objeto.tamanio}"
        if clave in objetos_revisados:
            # Si ya existe, agregar ambos a duplicados
            if objetos_revisados[clave] not in duplicados:
                duplicados.append(objetos_revisados[clave])
            duplicados.append(objeto)
        else:
            objetos_revisados[clave] = objeto
    
    # Crear sugerencias para duplicados
    sugerencias = []
    duplicados_procesados = set()
    
    for objeto in duplicados:
        clave = f"{objeto.nombre.lower().strip()}_{objeto.tipo}_{objeto.tamanio}"
        if clave not in duplicados_procesados:
            objetos_similares = [obj for obj in duplicados if f"{obj.nombre.lower().strip()}_{obj.tipo}_{obj.tamanio}" == clave]
            if len(objetos_similares) > 1:
                sugerencias.append({
                    'nombre': objeto.nombre,
                    'tipo': objeto.get_tipo_display(),
                    'tamanio': objeto.get_tamanio_display(),
                    'cantidad': len(objetos_similares),
                    'objetos': objetos_similares,
                    'clave': clave  # Para identificar el grupo de duplicados
                })
                duplicados_procesados.add(clave)
    
    context = {
        'caja': caja,
        'objetos': objetos,
        'orden_actual': orden,
        'duplicados': duplicados,
        'sugerencias': sugerencias,
        'total_objetos': objetos.count(),
        'porcentaje_ocupacion': round((objetos.count() / caja.capacidadMaxima) * 100, 1) if caja.capacidadMaxima > 0 else 0,
    }
    
    return render(request, 'detalle_caja.html', context)

def eliminar_objeto(request, objeto_id):
    """
    Vista para eliminar un objeto específico
    """
    if request.method == 'POST':
        try:
            objeto = Objeto.objects.get(id=objeto_id)
            cajas_afectadas = list(objeto.cajones.all())
            nombre_objeto = objeto.nombre
            
            # Registrar la acción antes de eliminar
            for caja in cajas_afectadas:
                registrar_accion(
                    tipo_accion='eliminar_objeto',
                    cajon=caja,
                    objeto=objeto,
                    descripcion=f'Se eliminó el objeto "{nombre_objeto}" de la caja "{caja.nombre}"'
                )
            
            # Eliminar el objeto
            objeto.delete()
            
            messages.success(request, f'Objeto "{nombre_objeto}" eliminado exitosamente.')
            
            # Redireccionar a la primera caja afectada o a crear caja si no hay cajas
            if cajas_afectadas:
                return redirect('detalle_caja', caja_id=cajas_afectadas[0].id)
            else:
                return redirect('crear_caja')
                
        except Objeto.DoesNotExist:
            messages.error(request, 'El objeto no existe.')
            return redirect('crear_caja')
        except Exception as e:
            messages.error(request, f'Error al eliminar el objeto: {str(e)}')
            return redirect('crear_caja')
    
    return redirect('crear_caja')

def eliminar_duplicados(request, caja_id):
    """
    Vista para eliminar objetos duplicados de una caja específica
    """
    if request.method == 'POST':
        try:
            caja = Cajon.objects.get(id=caja_id)
            objetos = caja.objetos.all()
            
            # Detectar duplicados
            objetos_revisados = {}
            duplicados_eliminados = []
            objetos_conservados = []
            
            for objeto in objetos:
                clave = f"{objeto.nombre.lower().strip()}_{objeto.tipo}_{objeto.tamanio}"
                if clave in objetos_revisados:
                    # Es un duplicado, lo marcamos para eliminar
                    duplicados_eliminados.append(objeto)
                else:
                    # Es el primero de su tipo, lo conservamos
                    objetos_revisados[clave] = objeto
                    objetos_conservados.append(objeto)
            
            # Eliminar los duplicados
            objetos_eliminados_nombres = []
            for objeto in duplicados_eliminados:
                objetos_eliminados_nombres.append(f"{objeto.nombre} ({objeto.get_tipo_display()}, {objeto.get_tamanio_display()})")
                
                # Registrar la acción antes de eliminar
                registrar_accion(
                    tipo_accion='eliminar_objeto',
                    cajon=caja,
                    objeto=objeto,
                    descripcion=f'Se eliminó el objeto duplicado "{objeto.nombre}" (tipo: {objeto.get_tipo_display()}, tamaño: {objeto.get_tamanio_display()}) de la caja "{caja.nombre}"'
                )
                
                objeto.delete()
            
            # Registrar la acción de limpieza general
            if duplicados_eliminados:
                registrar_accion(
                    tipo_accion='organizar_caja',
                    cajon=caja,
                    descripcion=f'Se eliminaron {len(duplicados_eliminados)} objetos duplicados de la caja "{caja.nombre}". Se conservaron {len(objetos_conservados)} objetos únicos.'
                )
                
                messages.success(request, f'Se eliminaron {len(duplicados_eliminados)} objetos duplicados. Se conservaron {len(objetos_conservados)} objetos únicos.')
            else:
                messages.info(request, 'No se encontraron objetos duplicados para eliminar.')
            
            return redirect('detalle_caja', caja_id=caja.id)
            
        except Cajon.DoesNotExist:
            messages.error(request, 'La caja no existe.')
            return redirect('crear_caja')
        except Exception as e:
            messages.error(request, f'Error al eliminar duplicados: {str(e)}')
            return redirect('detalle_caja', caja_id=caja_id)
    
    return redirect('crear_caja')

