from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('crear-caja/', views.crear_caja, name='crear_caja'),
                  path('añadir-objeto/', views.añadir_objeto, name='añadir_objeto'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
