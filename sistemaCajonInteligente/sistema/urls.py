from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('crear-caja/', views.crear_caja, name='crear_caja'),
    path('añadir-objeto/', views.añadir_objeto, name='añadir_objeto'),
    path('historial/', views.historial_acciones, name='historial_acciones'),
    path('caja/<int:caja_id>/', views.detalle_caja, name='detalle_caja'),
    path('eliminar-objeto/<int:objeto_id>/', views.eliminar_objeto, name='eliminar_objeto'),
    path('eliminar-duplicados/<int:caja_id>/', views.eliminar_duplicados, name='eliminar_duplicados'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
