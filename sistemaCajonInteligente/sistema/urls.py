from django.urls import path
from . import views

urlpatterns = [
    path('crear-caja/', views.crear_caja, name='crear_caja'),
]
