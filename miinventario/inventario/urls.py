from django.urls import path, include
from . import views

urlpatterns = [
    # Login personalizado
    path('login/', views.login_view, name='login'),

    # Django auth (logout, password reset, etc.)
    path('', include('django.contrib.auth.urls')),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),

    # Usuarios
    path('usuarios/', views.usuarios, name='usuarios'),
]
