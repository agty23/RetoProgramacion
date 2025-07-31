from django.urls import path
from . import views

urlpatterns = [
    path('crear-caja/', views.crear_caja, name='crear_caja'),
    path('añadir-objeto/', views.añadir_objeto, name='añadir_objeto'),
    path('historial/', views.historial_acciones, name='historial_acciones'),
]
