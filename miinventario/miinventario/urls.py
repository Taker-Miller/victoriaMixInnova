# miinventario/urls.py

from django.contrib import admin
from django.urls import path, include
from inventario.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='inicio'),  # Redirige la raíz al login
    path('inventario/', include('inventario.urls')),
]
